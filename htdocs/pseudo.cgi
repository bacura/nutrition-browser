#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 pseudo food editer 0.3.2 (2025/11/20)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#food_status = {1=>'user', 2=>'community',3=>'public', 9=>'original' }

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
		save:       "保存",
		delete:     "削除",
		food_name:  "食品名",
		food_n0:  	"食品番号",
		food_group: "食品群",
		notice: 	"備考：",
		weight:     "重量"
	}

	return l[language]
end

#
def add_fct_row( fct_collection, fct, disabled_option )
	fct_block = ''
	fct_collection.each do |e|
		picked_value = fct.pickt( e )
		t = picked_value.nil? || picked_value == '' ? 0.to_f : picked_value.to_f
		fct_block << "<tr><td>#{@fct_name[e]}</td><td align='right' width='20%'><input type='text' class='form-control form-control-sm' id='p#{e}' value=\"#{t}\" #{disabled_option}></td><td>#{@fct_unit[e]}</td></tr>"
	end

	return fct_block
end

#
def add_fct_row_cgi( fct_collection, cgi, disabled_option )
	fct_block = ''
	fct_collection.each do |e|
		fct_block << "<tr><td>#{@fct_name[e]}</td><td align='right' width='20%'><input type='text' class='form-control form-control-sm' id='p#{e}' value=\"#{cgi[e]}\" #{disabled_option}></td><td>#{@fct_unit[e]}</td></tr>"
	end

	return fct_block
end

#
def generate_food_no( db, food_group, prefix, food_base_no )
	puts 'generate_food_no<br>' if @debug
#	t = food_base_no.to_i <= 0 ? '' : food_base_no.to_s
	food_no = prefix + '001'

	food_status = 1
	food_status = 2 if prefix[0, 1] == 'C'
	food_status = 3 if prefix[0, 1] == 'P'

	query = "SELECT FN FROM #{$MYSQL_TB_TAG} WHERE FG=? AND FN=? AND status=?"
	condition = [food_group, food_no, food_status]
	if food_status == 1
		query += " AND user=?"
		condition << db.user.name
	end

	unless db.query( query, false, condition )&.first
		select_query = "SELECT FN FROM #{$MYSQL_TB_TAG} WHERE FG=? AND status=?"
		select_condition = [food_group, food_status]
		if food_status == 1
			select_query += " AND user=?"
			select_condition << db.user.name
		end

		fns = db.query( select_query, false, select_condition )&.map { |row| row['FN'] }
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


puts 'Getting POST<br>' if @debug
command = @cgi['command']

food_key = @cgi['food_key'].to_s
unless food_key.empty?
	fg_key, class1_key, class2_key, class3_key, food_name_key = food_key.split( ':' )
	food_group = fg_key
	class1 = class1_key
	class2 = class2_key
	class3 = class3_key
	food_name = food_name_key
else
	food_name = @cgi['food_name']
	food_group = @cgi['food_group']
	class1 = @cgi['class1']
	class2 = @cgi['class2']
	class3 = @cgi['class3']
	tag1 = @cgi['tag1']
	tag2 = @cgi['tag2']
	tag3 = @cgi['tag3']
	tag4 = @cgi['tag4']
	tag5 = @cgi['tag5']
end

food_weight = @cgi['food_weight']
food_weight_zero = food_weight == '0' ? true : false
food_weight = food_weight == nil || food_weight == ''|| food_weight == '0' ? 100 : BigDecimal( food_weight )

refuse = @cgi['REFUSE'].to_i
notice = @cgi['Notice']
switch = @cgi['food_no_unlock'].to_i

#
food_no = @cgi['food_no'].to_s
food_no = '' unless /\A[PCU]\d{5}\z/ =~ food_no

prefix = @cgi['prefix'].to_s
if prefix.to_s.empty? && food_no != ''
	prefix = food_no[0..2]
elsif prefix.to_s.empty?
	prefix = 'U' + food_group
end

#
food_base_no = @cgi['food_base_no'].to_s
if food_base_no.empty? && food_no != ''
	food_base_no = food_no[3..5]
elsif food_base_no == 'Auto'
	food_base_no = '000'
end

if @debug
	puts "command: #{command}<br>"
	puts "food_no: #{food_no}<br>"
	puts "food_key: #{food_key}<br>"
	puts "food_name: #{food_name}<br>"
	puts "food_group: #{food_group}<br>"
	puts "food_weight: #{food_weight}<br>"
	puts "prefix: #{prefix}<br>"
	puts "food_base_no: #{food_base_no}<br>"
	puts "switch: #{switch}<br>"
	puts "class1: #{class1}<br>"
	puts "class2: #{class2}<br>"
	puts "class3: #{class3}<br>"
	puts "tag1: #{tag1}<br>"
	puts "tag2: #{tag2}<br>"
	puts "tag3: #{tag3}<br>"
	puts "tag4: #{tag4}<br>"
	puts "tag5: #{tag5}<br>"
	puts "<hr>"
end


puts "Loading fctp<br>" if @debug
if command == 'init' && food_no != ''
	refuse, notice = fct.load_fctp( food_no )
	fct.calc
end


puts "Loading tag<br>" if @debug
tag_user = nil
if food_no != ''
	if command == 'init'
		res = db.query( "select * from #{$MYSQL_TB_TAG} WHERE FN=? AND ( user=? OR user=? )", false, [food_no, user.name, $GM] )&.first
		if res
			tag_user = res['user']
			class1 = res['class1']
			class2 = res['class2']
			class3 = res['class3']
			tag1 = res['tag1']
			tag2 = res['tag2']
			tag3 = res['tag3']
			tag4 = res['tag4']
			tag5 = res['tag5']
			food_status = res['status'].to_i
		end

	elsif command == 'save' || command == 'switch'
		res = db.query(  "select * from #{$MYSQL_TB_TAG} WHERE FN=? AND user=?", false, [food_no, user.name] )&.first
		tag_user = res['user'] if res
	end
end

move_flag = false
if command == 'save'
	puts "SAVE:" if @debug
	fct.load_cgi( @cgi )

	if  @cgi['ENERC_KCAL'].to_f != 0 && @cgi['ENERC'].to_f == 0
		puts "Energy>" if @debug
		fct.put_solid( 'ENERC', 0, (( @cgi['ENERC_KCAL'].to_f * 4184 ) / 1000 ).to_i )
	end
	if  @cgi['NACL_EQ'].to_f != 0 && @cgi['NA'].to_f == 0
		puts "Na>" if @debug
		fct.put_solid( 'NA', 0, ( @cgi['NACL_EQ'].to_f / 2.54 ).round( 1 ))
	end

	fct.singlet
	fct.gramt( 100 )
	fct.digit

	# ゼロ重量戻し
	food_weight = 0 if food_weight_zero
	class1_new = class1.empty? ? '' : "＜#{class1}＞"
	class2_new = class2.empty? ? '' : "［#{class2}］"
	class3_new = class3.empty? ? '' : "（#{class3}）"
	tag1_new = tag1.empty? ? '' : "　#{tag1}"
	tag2_new = tag2.empty? ? '' : "　#{tag2}"
	tag3_new = tag3.empty? ? '' : "　#{tag3}"
	tag4_new = tag4.empty? ? '' : "　#{tag4}"
	tag5_new = tag5.empty? ? '' : "　#{tag5}"
	tagnames_new = "#{class1_new}#{class2_new}#{class3_new}#{food_name}#{tag1_new}#{tag2_new}#{tag3_new}#{tag4_new}#{tag5_new}"

	puts 'Generate units<br>' if @debug
	unith = Hash.new
	unith['g'] = 1
	unith['kcal'] = ( fct.pickt( 'ENERC_KCAL' ) / 100 ).to_i if fct.pickt( 'ENERC_KCAL' ) != 0
	unith['g処理前'] = (( 100 - refuse ) / 100 ).to_i if refuse != 0
	unit = JSON.generate( unith.sort.to_h )

	fct_set = "REFUSE='#{refuse}', #{fct.sql}, Notice='#{notice}'"

	puts 'Generate food number<br>' if @debug
	if switch == 0
		food_no_new = generate_food_no( db, food_group, prefix, '001' )
	else
		food_no_new = prefix + food_base_no 
	end
	move_flag = true if food_no_new != food_no && food_no != ''

	puts 'Checking Food number<br>' if @debug
	if db.query(  "select FN from #{$MYSQL_TB_TAG} WHERE user=? AND FN=?", false, [user.name, food_no] )&.first
		db.query(  "UPDATE #{$MYSQL_TB_TAG} SET FG=?,name=?,class1=?,class2=?,class3=?,tag1=?,tag2=?,tag3=?,tag4=?,tag5=?,status=? WHERE FN=? AND user=?", true, [food_group, food_name, class1, class2, class3, tag1, tag2, tag3, tag4, tag5, status, food_no, user.name] )
	else
		db.query(  "INSERT INTO #{$MYSQL_TB_TAG} SET FG=?,SID='',name=?,class1=?,class2=?,class3=?,tag1=?,tag2=?,tag3=?,tag4=?,tag5=?,status=?,FN=?,user=?", true, [food_group, food_name, class1, class2, class3, tag1, tag2, tag3, tag4, tag5, status, food_no, user.name ] )
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

	food_weight = 100
	tag_user = user.name
end


puts "Deleting pseudo food<br>" if @debug
if command == 'delete' || move_flag
	puts "DELETE<br>" if @debug
	res = db.query( "SELECT FG, name FROM #{$MYSQL_TB_TAG} WHERE user=? AND FN=?", false, [user.name, food_no] )&.first
	db.query(  "DELETE FROM #{$MYSQL_TB_DIC} WHERE user=? AND FG=? AND org_name", true, [user.name, res['FG'], res['name'] ) if res

	db.query(  "DELETE FROM #{$MYSQL_TB_TAG} WHERE user=? AND FN=?", true, [user.name, food_no] )
	db.query(  "DELETE FROM #{$MYSQL_TB_FCTP} WHERE user=? AND FN=?", true, [user.name, food_no] )
	db.query(  "DELETE FROM #{$MYSQL_TB_EXT} WHERE user=? AND FN=?", true, [user.name, food_no] )

	unless move_flag
		prefix = ''
		food_base_no = ''
		food_no = ''
	else
		food_no = prefix + food_base_no 
	end
end


puts "FCT block html<br>" if @debug
food_group_option = ''
@category.size.times do |c| food_group_option << "<option value='#{@fg[c]}' #{$SELECT[food_group.to_i == c]}>#{c}.#{@category[c]}</option>" end
disabled_option = tag_user != user.name && tag_user != nil && user.status != 9 ? 'disabled' : ''

fct_block = Array.new( 6, '' )
if command == 'switch'
	fct_block[0] = add_fct_row_cgi( @fct_rew, @cgi, disabled_option )
	fct_block[1] = add_fct_row_cgi( @fct_pf, @cgi, disabled_option )
	fct_block[2] = add_fct_row_cgi( @fct_cho, @cgi, disabled_option )
	fct_block[3] = add_fct_row_cgi( @fct_m, @cgi, disabled_option )
	fct_block[4] = add_fct_row_cgi( @fct_fsv, @cgi, disabled_option )
	fct_block[5] = add_fct_row_cgi( @fct_wsv, @cgi, disabled_option )
	fct_block[5] << "<tr><td><hr></td></tr>"
	fct_block[5] << add_fct_row_cgi( @fct_as, @cgi, disabled_option )
else
	fct_block[0] = add_fct_row( @fct_rew, fct, disabled_option )
	fct_block[1] = add_fct_row( @fct_pf, fct, disabled_option )
	fct_block[2] = add_fct_row( @fct_cho, fct, disabled_option )
	fct_block[3] = add_fct_row( @fct_m, fct, disabled_option )
	fct_block[4] = add_fct_row( @fct_fsv, fct, disabled_option )
	fct_block[5] = add_fct_row( @fct_wsv, fct, disabled_option )
	fct_block[5] << "<tr><td><hr></td></tr>"
	fct_block[5] << add_fct_row( @fct_as, fct, disabled_option )
end

puts "ports html<br>" if @debug
save_button = tag_user == user.name || food_no == '' ? "<button class=\"btn btn-outline-primary btn-sm\" type=\"button\" onclick=\"pseudoSave()\">#{l[:save]}</button>" : ''
delete_button = tag_user == user.name && food_no != '' ? "<button class='btn btn-outline-danger btn-sm' type='button' onclick=\"pseudoDelete( '#{food_no}' )\">#{l[:delete]}</button>" : ''
fg_disabled = food_no != '' ? "DISABLED" : ''

prefix_option = "<option value='U#{food_group}'>U#{food_group}</option>"
#prefix_option << "<option value='C#{food_group}' #{$SELECT[prefix[0, 1]=='C']}>C#{food_group}</option>" if user.status >= 8 
prefix_option << "<option value='P#{food_group}' #{$SELECT[prefix[0, 1]=='P']}>P#{food_group}</option>" if user.status >= 8 && $NBURL == $MYURL


if food_no != ''
	if switch == 0
		if prefix == food_no[0..2]
			food_base_no = food_no[3..5]
		else
#			food_base_no = generate_food_no( db, food_group, prefix, '000' )[3..5]
			food_base_no = 'Auto'
		end
	else
		food_base_no = '001' if food_base_no == '' || food_base_no == '000'
	end
else
	if switch == 0
#		food_base_no = generate_food_no( db, food_group, prefix, '000' )[3..5]
		food_base_no = 'Auto'
	else
		food_base_no = '001' if food_base_no == '' || food_base_no == '000'
	end
end


puts "HTML<br>" if @debug
html = <<~HTML
<div class='container-fluid'>
	<div class="row">
		<div class="col-2">
			<div class="input-group input-group-sm">
				<select class="form-select" id="pfood_group" #{fg_disabled}>
					#{food_group_option}
				</select>
			</div>
		</div>
		<div class="col-2">
			<div class="input-group input-group-sm">
				<select class="form-select" id="pprefix" onChange="switchPrefix()">
					#{prefix_option}
				</select>
				<input type="text" class="form-control form-control-sm" id="pfood_base_no" placeholder="#{l[:food_no]}" value="#{food_base_no}" #{$DISABLE[switch!=1]}>
				&nbsp;
				<div class="form-check form-switch">
					<input class="form-check-input" type="checkbox" id="food_no_unlock" #{$CHECK[switch==1]} onChange="switchPrefix()">
				</div>
			</div>
		</div>
		<div class="col-3">
			<input type="text" class="form-control form-control-sm" id="pfood_name" placeholder="#{l[:food_name]}" value="#{food_name}">
		</div>
		<div class="col-1"></div>
		<div class="col-2">
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="food_weight">#{l[:weight]}</label>
				<input type="text" class="form-control form-control-sm" id="pfood_weight" placeholder="100" value="#{food_weight.to_f}">&nbsp;g
			</div>
		</div>
		<div class="col-1"></div>
		<div class="col-1">
			#{save_button}
		</div>
	</div>

	<br>
	<div class="row">
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="pclass1" placeholder="class1" value="#{class1}"></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="pclass2" placeholder="class2" value="#{class2}"></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="pclass3" placeholder="class3" value="#{class3}"></div>
	</div>
	<br>
	<div class="row">
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="ptag1" placeholder="tag1" value="#{tag1}"></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="ptag2" placeholder="tag2" value="#{tag2}"></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="ptag3" placeholder="tag3" value="#{tag3}"></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="ptag4" placeholder="tag4" value="#{tag4}"></div>
		<div class="col-2"><input type="text" class="form-control form-control-sm" id="ptag5" placeholder="tag5" value="#{tag5}"></div>
		<div class="col-1"></div>
		<div class="col-1">#{delete_button}</div>
	</div>
	<hr>
	<div class="row">
		<div class="col-4">
			<table class="table-sm table-striped" width="100%">#{fct_block[0]}</table>

			<div style='border: solid gray 1px; margin: 0.5em; padding: 0.5em;'>
				#{l[:notice]}<br>
				<textarea rows="6" cols="32" id="pNotice" #{disabled_option}>#{notice}</textarea>
			</div>
		</div>

		<div class="col-4">
			<table class="table-sm table-striped" width="100%">#{fct_block[1]}</table>
		</div>

		<div class="col-4">
			<table class="table-sm table-striped" width="100%">#{fct_block[2]}</table>
		</div>
	</div>

	<hr>

	<div class="row">
		<div class="col-4">
			<table class="table-sm table-striped" width="100%">#{fct_block[3]}</table>
		</div>

		<div class="col-4">
			<table class="table-sm table-striped" width="100%">#{fct_block[4]}</table>
		</div>

		<div class="col-4">
			<table class="table-sm table-striped" width="100%">#{fct_block[5]}</table>
		</div>
	</div>
	<div class='code'>#{food_no}</div>
	<input type="hidden" id="food_no" value='#{food_no}'>
</div>


HTML

puts html


#==============================================================================
# FRONT SCRIPT START
#==============================================================================

if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

//Get from DOM values
var getValue = ( id ) => document.getElementById( id ).value;

// Get all fields
var getFields = () => {
	const fields = [
		"prefix", "food_base_no", "food_name", "food_group", "food_weight", "class1", "class2", "class3",
		"tag1", "tag2", "tag3", "tag4", "tag5", "REFUSE", "ENERC", "ENERC_KCAL", "WATER",
		"PROTCAA", "PROT", "PROTV", "FATNLEA", "CHOLE", "FAT", "FATV", "CHOAVLM", "CHOAVL", 
		"CHOAVLDF", "CHOV", "FIB", "POLYL", "CHOCDF", "OA", "ASH", "NA", "K", "CA", "MG", 
		"P", "FE", "ZN", "CU", "MN", "ID", "SE", "CR", "MO", "RETOL", "CARTA", "CARTB", 
		"CRYPXB", "CARTBEQ", "VITA_RAE", "VITD", "TOCPHA", "TOCPHB", "TOCPHG", "TOCPHD", 
		"VITK", "THIA", "RIBF", "NIA", "NE", "VITB6A", "VITB12", "FOL", "PANTAC", "BIOT", 
		"VITC", "ALC", "NACL_EQ", "Notice", "FASAT", "FAMS", "FAPU", "FAPUN3", "FAPUN6", 
		"FIBTG", "FIBSOL", "FIBINS", "FIBTDF", "FIBSDFS", "FIBSDFP", "FIBIDF", "STARES"
	];

	let data = {};
	fields.forEach( field => { data[field] = getValue( "p" + field );});

	const foodNoUnlock = document.getElementById( "food_no_unlock" );
  	data.food_no_unlock = foodNoUnlock && foodNoUnlock.checked ? 1 : 0;

	data.food_no = document.getElementById( "food_no" ).value;

	return data;
};


//Save pseudo food
var switchPrefix = function() {
	const data = getFields();

	postLayer( '#{myself}', "switch", true, "LF", data );
};


//Save pseudo food
var pseudoSave = function() {
	const data = getFields();

	if ( data.food_name !== '' ) {
		postLayer( '#{myself}', "save", true, "LF", data );
		displayVIDEO( data.food_name + ' saved' );
	} else {
		displayVIDEO('Food name! (>_<)');
	}
};


//Delete  pseudo food
var pseudoDelete = ( food_no ) => {
	postLayer( '#{myself}', "delete", true, "LF", { food_no });

	dlf = false;
	displayBW();
	displayVIDEO( food_no + ' deleted' );
};

</script>

JS
	puts js
end
