#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser recipe to pseudo food 0.2.5 (2025/10/04)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require './brain'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['jp'] = {
		save:		"保存",
		food_name:	"食品名",
		food_group:	"食品群",
		food_range:	"有効範囲"
	}

	return l[language]
end

def generate_food_no( db, food_group, prefix, food_base_no )
	puts 'generate_food_no<br>' if @debug
#	t = food_base_no.to_i <= 0 ? '' : food_base_no.to_s
	food_no = prefix + '001'

	food_status = 1
	food_status = 2 if prefix[0, 1] == 'C'
	food_status = 3 if prefix[0, 1] == 'P'

	query = "SELECT FN FROM #{$MYSQL_TB_TAG} WHERE FG=? AND FN=? AND status=?"
	condition = [food_group, food_no, status]
	if status == 1
		query += " AND user=?"
		condition << db.user.name
	end

	unless db.query( query, false, condition )&.first
		select_query = "SELECT FN FROM #{$MYSQL_TB_TAG} WHERE FG=? AND status=?"
		select_condition = [food_group, status]
		if status == 1
			select_query += " AND user=?"
			select_condition << db.user.name
		end

		fns = db.query(select_query, false, select_condition)&.map { |row| row['FN'] }
		( 1..999 ).each do |i|
			candidate = prefix + "%03d" % i
			return candidate unless fns&.include?( candidate )
		end
		rise( 'error 999' )
	end

	food_no
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )

fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
fct.load_palette( @palette_bit_all )

puts 'POST data<br>' if @debug
command = @cgi['command'].to_s
recipe_code = @cgi['code'].to_s
food_name = @cgi['food_name'].to_s
food_group = @cgi['food_group'].to_s
prefix = @cgi['prefix'].to_s + food_group
class1 = @cgi['class1'].to_s
class2 = @cgi['class2'].to_s
class3 = @cgi['class3'].to_s
tag1 = @cgi['tag1'].to_s
tag2 = @cgi['tag2'].to_s
tag3 = @cgi['tag3'].to_s
tag4 = @cgi['tag4'].to_s
tag5 = @cgi['tag5'].to_s
if @debug
	puts "command: #{command}<br>\n"
	puts "recipe_code: #{recipe_code}<br>\n"
	puts "<hr>\n"
	puts "food_name: #{food_name}<br>\n"
	puts "food_group: #{food_group}<br>\n"
	puts "class1: #{class1}<br>\n"
	puts "class2: #{class2}<br>\n"
	puts "class3: #{class3}<br>\n"
	puts "tag1: #{tag1}<br>\n"
	puts "tag2: #{tag2}<br>\n"
	puts "tag3: #{tag3}<br>\n"
	puts "tag4: #{tag4}<br>\n"
	puts "tag5: #{tag5}<br>\n"
end


puts 'Extracting SUM<br>' if @debug
res = db.query(  "SELECT code, name, sum, dish from #{$MYSQL_TB_SUM} WHERE user=?", false, [user.name] )&.first
if res
	food_name = res['name'] if food_name == ''
	recipe_code = res['code']
	dish_num = res['dish'].to_i
	food_no, food_weight = extract_sum( res['sum'], dish_num, 0 )[0..1]
end

if command == 'init'
	puts 'Generate form HTML<br>' if @debug
	food_group_option = ''
	@category.size.times do |c| food_group_option << "<option value='#{@fg[c]}'>#{c}.#{@category[c]}</option>" end

	food_range_option = "<option value='U'>U</option>"
#	food_range_option << "<option value='C'>U</option>" if user.status >= 8 
	food_range_option << "<option value='P'>P</option>" if user.status >= 8 && $NBURL == $MYURL

	html = <<~HTML
<div class='container-fluid'>
	<div class="row">
		<div class="col-3">
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="food_group">#{l[:food_group]}</label>
				<select class="form-select form-select-sm" id="r2ffood_group">
					#{food_group_option}
				</select>
			</div>
		</div>
		<div class="col-2">
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="r2fprefix">#{l[:food_range]}</label>
				<select class="form-select form-select-sm" id="r2fprefix">
					#{food_range_option}
				</select>
			</div>
		</div>
		<div class="col-4">
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="food_name">#{l[:food_name]}</label>
				<input type="text" class="form-control form-control-sm" id="r2ffood_name" value="#{food_name}">
			</div>
		</div>
		<div class="col-2"></div>
		<div class="col-1">
			<button class="btn btn-outline-primary btn-sm" type="button" onclick="savePseudo_R2F( '#{recipe_code}' )">#{l[:save]}</button>
		</div>
	</div>

	<br>
	<div class="row">
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="r2fclass1" placeholder="class1" value=""></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="r2fclass2" placeholder="class2" value=""></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="r2fclass3" placeholder="class3" value=""></div>
	</div>
	<br>
	<div class="row">
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="r2ftag1" placeholder="tag1" value=""></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="r2ftag2" placeholder="tag2" value=""></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="r2ftag3" placeholder="tag3" value=""></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="r2ftag4" placeholder="tag4" value=""></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="r2ftag5" placeholder="tag5" value=""></div>
		<div class="col-1"></div>
	</div>
</div>

HTML
end


if command == 'save'
	puts 'FCT Calc<br>' if @debug
	fct.set_food( food_no, food_weight, false )
	fct.calc
	fct.gramt( 100 )
	fct.digit

	class1_new = class1.empty? ? '' : "＜#{class1}＞"
	class2_new = class2.empty? ? '' : "＜#{class2}＞"
	class3_new = class3.empty? ? '' : "＜#{class3}＞"
	tag1_new = tag1.empty? ? '' : "　#{tag1}"
	tag2_new = tag2.empty? ? '' : "　#{tag2}"
	tag3_new = tag3.empty? ? '' : "　#{tag3}"
	tag4_new = tag4.empty? ? '' : "　#{tag4}"
	tag5_new = tag5.empty? ? '' : "　#{tag5}"
	tagnames_new = "#{class1_new}#{class2_new}#{class3_new}#{food_name}#{tag1_new}#{tag2_new}#{tag3_new}#{tag4_new}#{tag5_new}"

	puts 'Generate units<br>' if @debug
	unith = Hash.new
	unith['g'] = 1
	unith['kcal'] = fct.pickt( 'ENERC_KCAL' ).to_f / 100 if fct.pickt( 'ENERC_KCAL' ) != 0
	unith_ = unith.sort.to_h
	unit = JSON.generate( unith_ )

	fct_set = "REFUSE='0', #{fct.sql}, Notice='#{recipe_code}'"

	puts 'Generate food number<br>' if @debug
	food_no = generate_food_no( db, food_group, prefix, '001' )

	puts 'Checking Food number<br>' if @debug
	unless food_no.empty?
		status = 1
		status = 2 if prefix[0, 1] == 'C'
		status = 3 if prefix[0, 1] == 'P'


		if db.query(  "select FN from #{$MYSQL_TB_TAG} WHERE user=? AND FN=?", false, [user.name, food_no] )&.first
			db.query(  "UPDATE #{$MYSQL_TB_TAG} SET FG=?, name=?, class1=?, class2=?, class3=?, tag1=?, tag2=?, tag3=?, tag4=?, tag5=?, status=? WHERE FN=? AND user=?", true, [food_group, food_name, class1, class2, class3, tag1, tag2, tag3, tag4, tag5, status, food_no, user.name] )
		else
			db.query(  "INSERT INTO #{$MYSQL_TB_TAG} SET FG=?, SID='', name=?, class1=?, class2=?, class3=?, tag1=?, tag2=?, tag3=?, tag4=?, tag5=?, status=?, FN=?, user=?", true, [food_group, food_name, class1, class2, class3, tag1, tag2, tag3, tag4, tag5, status, food_no, user.name ] )
	 	end

		if db.query(  "select FN from #{$MYSQL_TB_FCTP} WHERE user=? AND FN=?", false, [user.name, food_no] )&.first
			db.query(  "UPDATE #{$MYSQL_TB_FCTP} SET FG=?, Tagnames=?, #{fct_set} WHERE FN=? AND user=?", true, [food_group, tagnames_new, food_no, user.name] )
		else
			db.query(  "INSERT INTO #{$MYSQL_TB_FCTP} SET FG=?, Tagnames=?, #{fct_set}, FN=?, user=?", true, [food_group, tagnames_new, food_no, user.name])
		end

		if db.query(  "select FN from #{$MYSQL_TB_EXT} WHERE user=? AND FN=?", false, [user.name, food_no] )&.first
			db.query(  "UPDATE #{$MYSQL_TB_EXT} SET color1='0', color2='0', color1h='0', color2h='0', unit=? WHERE FN=? AND user=?", true, [unit, food_no, user.name] )
		else
			db.query(  "INSERT INTO #{$MYSQL_TB_EXT} SET  color1='0', color2='0', color1h='0', color2h='0', unit=?,FN=?, user=?", true, [unit, food_no, user.name] )
		end
	end
end

puts html

#==============================================================================
# FRONT SCRIPT START
#==============================================================================

if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

// 食品化フォームの保存ボタンを押して保存してL3を消す。
var savePseudo_R2F = ( code ) => {
	const fieldList = [ "food_name", "food_group", "prefix", "class1", "class2", "class3", "tag1", "tag2", "tag3","tag4","tag5" ];
	let data = getDOMdata( fieldList, 'r2f' );
	data.code = code;

	if( data.food_name != '' ){
		postLayer( '#{myself}', "save", true, "L2", data );

		displayVIDEO( 'Foodized' );

		dl2 = false;
		displayBW();
	}else{
		displayVIDEO( 'Food name! (>_<)' );
	}
};

</script>

JS
	puts js
end
