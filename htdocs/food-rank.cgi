#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 food ranking 0.1.1 (2026/01/13)


#==============================================================================
#LIBRARY
#==============================================================================
require './soul'


#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )


#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		main:	"主成分",
		comp:	"比較成分",
		g100:	"100gあたり",
		kou: 	"降順",
		shou: 	"昇順",
		sort: 	"並べる",
		rank:	"順位",
		fn:		"食品番号",
		food_name:	"食品名",
		ratio:	"比率",
		search:	"レシピ検索",
		fg:		"食品群",
		num:		"表示数",
		ex_inf:		"∞を除外",
		ex_zero:	"0を除外 (0/0含む)",
		order:		"並び",
		fg_all:		"すべて"
	}

	return l[language]
end


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )


#### POST
command = @cgi['command']
ex_inf = @cgi['ex_inf'].to_i
ex_zero = @cgi['ex_zero'].to_i
fg = @cgi['fg'].to_i
p command, ex_inf, ex_zero, '<hr>' if @debug


main_item = 'ENERC_KCAL'
comp_item = 'weight'
rank_order = 0
rank_display = 50

list_html = ''
if command == 'list'
	puts 'Lsit<br>' if @debug
	main_item = @cgi['main_item'].to_s
	comp_item = @cgi['comp_item'].to_s

	rank_order = @cgi['rank_order'].to_i
	rank_display = @cgi['rank_display'].to_i
	p main_item, comp_item, rank_order, rank_display, '<hr>' if @debug

	comp_sql = nil
	comp_flag = false
	if comp_item != 'weight' && comp_item != ''
		comp_sql = ", #{comp_item}"
		comp_flag = true
	end

	if fg == 0
		r = db.query( "SELECT FN, #{main_item} #{comp_sql} FROM #{$TB_FCT};", false )
	else
		sql_fg = fg
		sql_fg = "0#{fg}" if sql_fg < 10
		r = db.query( "SELECT FN, #{main_item} #{comp_sql} FROM #{$TB_FCT} WHERE FG=?", false, [sql_fg] )
	end
	main_value = Hash.new
	comp_value = Hash.new
	ratio = Hash.new

	puts 'Zero process<br>' if @debug
	r.each do |r|
		food_no = r['FN']
		main_value[food_no] = BigDecimal( convert_zero( r[main_item] ).to_s )
		if comp_flag
			comp_value[food_no] =  BigDecimal( convert_zero( r[comp_item] ).to_s )
			if comp_value[food_no] != 0
				# normal
				ratio[food_no] = ( main_value[food_no] / comp_value[food_no] ).round( 4 )
			elsif main_value[food_no] == 0 && comp_value[food_no] == 0
				# zero / zero
				ratio[food_no] = 0
			else
				#infinity
				ratio[food_no] = 99999999
			end
		else
			comp_value[food_no] = 1
			ratio[food_no] = main_value[food_no]
		end
	end
	a = ratio.sort_by do |_, v| v end
	a.reverse! if rank_order == 0
	ratio = a.to_h

	puts 'Rank HTML<br>' if @debug
	list_html = '<table class="table table-sm">'
	list_html << '<thead>'
	list_html << '<tr>'
	list_html << "<td>#{l[:rank]}</td><td>#{l[:fn]}</td><td>#{l[:food_name]}</td><td>#{@fct_name[main_item]}</td><td>#{@fct_name[comp_item]}</td><td>#{l[:ratio]}</td><td>&nbsp;</td>"
	list_html << '</tr>'
	list_html << '</thead>'

	food_tag = Hash.new
	rr = db.query( "SELECT * FROM #{$TB_TAG};", false )
	rr.each do |rr| food_tag[rr['FN']] = rr end

	recipei = Hash.new
	rr = db.query( "SELECT word FROM #{$TB_RECIPEI} WHERE user=? OR public=1;", false, [user.name] )
	rr.each do |rr| recipei[rr['word']] = true end

	count = 1
	ratio.each do |k, v|
		sub_class = ''
		sub_class << food_tag[k]['class1'].sub( '+', '' ) if /\+$/ =~ food_tag[k]['class1']
		sub_class << food_tag[k]['class2'].sub( '+', '' ) if /\+$/ =~ food_tag[k]['class2']
		sub_class << food_tag[k]['class3'].sub( '+', '' ) if /\+$/ =~ food_tag[k]['class3']
		food_name = food_tag[k]['name']
		tag1 = food_tag[k]['tag1']
		tag2 = food_tag[k]['tag2']
		tag3 = food_tag[k]['tag3']
		tag4 = food_tag[k]['tag4']
		tag5 = food_tag[k]['tag5']
		tags = "<span class='tagc'>#{sub_class}</span> #{food_name} <span class='tag1'>#{tag1}</span> <span class='tag2'>#{tag2}</span> <span class='tag3'>#{tag3}</span> <span class='tag4'>#{tag4}</span> <span class='tag5'>#{tag5}</span>"

		recipe_serch = ''
		recipe_serch = "<span class='badge bg-info text-dark' onclick=\"searchDR( '#{food_name}' )\">#{l[:search]}</span>" if recipei[food_name] == true && user.status >= 1

		unless ( v == 99999999 && ex_inf == 1 ) || ( v == 0 && ex_zero == 1 )
			list_html << '<tr>'
			list_html << "<td>#{count}</td>"
			list_html << "<td>#{k}</td>"
			list_html << "<td class='link_cursor' onclick=\"detailView_his( '#{k}' )\">#{tags}</td>"
			list_html << "<td>#{main_value[k].to_f}</td>"
			list_html << "<td>#{comp_value[k].to_f}</td>"

			if v == 99999999
				list_html << "<td>∞</td>"
			else
				list_html << "<td>%.4f</td>" % v.to_f
			end

			list_html << "<td>#{recipe_serch}</td>"
			list_html << '</tr>'
		end

		break if count == rank_display
		count += 1
	end
	list_html << '</table>'
end


####
puts 'Food group select-HTML<br>' if @debug
fg_select = '<select class="form-select" id="fg">'
@category.each.with_index do |e, i|
	if i == 0
		fg_select << "<option value='#{i}' #{$SELECT[i == fg]}>#{l[:fg_all]}</option>"
	elsif i == 19
	else
		fg_select << "<option value='#{i}' #{$SELECT[i == fg]}>#{e}</option>"
	end
end
fg_select << '</select>'


####
puts 'Main item select-HTML<br>' if @debug
main_item_select = '<select class="form-select" id="main_item">'
@fct_item.each do |e|
	unless e == 'FG' || e == 'FN' || e == 'SID' || e == 'Tagnames' || e == 'REFUSE' || e == 'Notice'
		main_item_select << "<option value='#{e}' #{$SELECT[e == main_item]}>#{@fct_name[e]}</option>"
	end
end
main_item_select << '</select>'


####
puts 'Comp item select-HTML<br>' if @debug
comp_item_select = '<select class="form-select" id="comp_item">'
comp_item_select << "<option value='weight'>#{l[:g100]}</option>"
@fct_item.each do |e|
	unless e == 'FG' || e == 'FN' || e == 'SID' || e == 'Tagnames' || e == 'REFUSE' || e == 'Notice'
		comp_item_select << "<option value='#{e}' #{$SELECT[e == comp_item]}>#{@fct_name[e]}</option>"
	end
end
comp_item_select << '</select>'


####
rank_order_select = '<select class="form-select form-select-sm" id="rank_order">'
if rank_order == 0
	rank_order_select << "<option value='0' SELECTED>#{l[:shou]}</option>"
	rank_order_select << "<option value='1'>#{l[:kou]}</option>"
else
	rank_order_select << "<option value='0'>#{l[:shou]}</option>"
	rank_order_select << "<option value='1' SELECTED>#{l[:kou]}</option>"
end
rank_order_select << '</select>'


####
rank_nums = [ 50,  100,  500, 1000, 2000, 3000 ]
rank_nums_ = [ '50', '100',  '500', '1000', '2000', 'all' ]
rank_display_select = '<select class="form-select" id="rank_display">'
rank_nums.size.times do |c|
	rank_display_select << "<option value='#{rank_nums[c]}' #{$SELECT[rank_display == rank_nums[c]]}>#{rank_nums_[c]}</option>"
end


puts "Control HTML<br>" if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-2'>
			<div class="input-group input-group-sm mb-3">
				<label class="input-group-text">#{l[:fg]}</label>
				#{fg_select}
			</div>
		</div>
		<div class='col-4'>
			<div class="input-group input-group-sm mb-3">
				<label class="input-group-text">#{l[:main]}</label>
				#{main_item_select}
			</div>
		</div>
		<div class='col-4'>
			<div class="input-group input-group-sm mb-3">
				<label class="input-group-text">#{l[:comp]}</label>
				#{comp_item_select}
			</div>
		</div>
		<div class='col-2'>
			<div class="input-group input-group-sm mb-3">
				<label class="input-group-text">#{l[:order]}</label>
				#{rank_order_select}
			</div>
		</div>
	</div>
	<div class='row'>
		<div class='col-2'>
			<div class="input-group input-group-sm">
			<label class="input-group-text">#{l[:num]}</label>
			<select class="form-select" id="rank_display">
				<option value="50">50</option>
				<option value="100">100</option>
				<option value="500">500</option>
				<option value="1000">1000</option>
				<option value="2000">2000</option>
				<option value="3000">all</option>
			</select>
			</div>
		</div>
		<div class='col-2'>
			<div class="form-check">
				<input class="form-check-input" type="checkbox" id="ex_inf" #{$CHECK[ex_inf == 1]}>
				<label class="form-check-label">#{l[:ex_inf]}</label>
			</div>
		</div>
		<div class='col-3'>
			<div class="form-check">
				<input class="form-check-input" type="checkbox" id="ex_zero" #{$CHECK[ex_zero == 1]}>
				<label class="form-check-label">#{l[:ex_zero]}</label>
			</div>
		</div>
		<div class='col' align="right">
			<button class="btn btn-outline-primary btn-sm" type="button" onclick="foodRankList()">#{l[:sort]}</button>
		</div>
	</div>
	<br>
	<div class='row'>
	#{list_html}
	</div>
</div>
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================


#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

// Dosplaying recipe by scatter plott
var foodRankList = () => {
	const main_item = document.getElementById( "main_item" ).value;
	const comp_item = document.getElementById( "comp_item" ).value;
	const rank_order = document.getElementById( "rank_order" ).value;
	const rank_display = document.getElementById( "rank_display" ).value;
	const fg = document.getElementById( "fg" ).value;

	const ex_infif = document.getElementById( "ex_inf" ).checked ? 1 : 0;
	const ex_zeroif = document.getElementById( "ex_zero" ).checked ? 1 : 0;

	postLayer( '#{myself}', 'list', true, 'L1', { fg, main_item, comp_item, rank_order, rank_display, ex_inf, ex_zero });
};

</script>

JS

	puts js
end
