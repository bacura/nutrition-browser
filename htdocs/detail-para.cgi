#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 food detail parallel 0.0.2 (2024/10/12)


#==============================================================================
# STATIC
#==============================================================================
@debug = false
#script = File.basename( $0, '.cgi' )

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		'weight' 	=> "重量",\
		'fn' 		=> "食品番号",\
		'name' 		=> "食品名",\
		'juten' 	=> "重点",\
		'flat' 		=> "均等",\
		'change'	=> "<img src='bootstrap-dist/icons/hammer.svg' style='height:1.2em; width:1.2em;'>",\
		'signpost'	=> "<img src='bootstrap-dist/icons/signpost-r.svg' style='height:2em; width:2em;'>",
		'parallel'	=> "<img src='bootstrap-dist/icons/wrench-adjustable.svg' style='height:2em; width:2em;'>"
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
food_key = @cgi['food_key']
frct_mode = @cgi['frct_mode'].to_i
food_weight = @cgi['food_weight']
food_no = @cgi['food_no']
base = @cgi['base']
base_fn = @cgi['base_fn']
juten = @cgi['juten'].to_s
juten = 'ENERC_KCAL' if juten == ''
if @debug
	puts "food_key: #{food_key}<br>"
	puts "frct_mode: #{frct_mode}<br>"
	puts "food_weight: #{food_weight}<br>"
	puts "food_no: #{food_no}<br>"
	puts "base: #{base}<br>"
	puts "base_fn: #{base_fn}<br>"
	puts "juten: #{juten}<br>"
	puts "<hr>"
end


puts 'Key chain<br>' if @debug
food_key = '' if food_key == nil
fg_key, class1, class2, class3, food_name = food_key.split( ':' )

class_name = ''
class_no = 0
unless class1 == nil || class1 == ''
	class_name = class1
	class_no = 1
end
unless class2 == nil || class2 == ''
	class_name = class2
	class_no = 2
end
unless class3 == nil || class3 == ''
	class_name = class3
	class_no = 3
end
if @debug
	puts "fg_key: #{fg_key}<br>"
	puts "class1: #{class1}<br>"
	puts "class2: #{class2}<br>"
	puts "class3: #{class3}<br>"
	puts "class_no: #{class_no}<br>"
	puts "class_name: #{class_name}<br>"
	puts "<hr>"
end


#### 閲覧選択
html = ''


case command
when 'init', 'weight', 'cb', 'cbp'
	puts 'L2 final page<br>' if @debug
	require './brain'

	food_weight = BigDecimal( food_weight_check( food_weight ).first )

	query = ''
	food_no_list = []
	food_name_list = []
	tag1_list = []
	tag2_list = []
	tag3_list = []
	tag4_list = []
	tag5_list = []
	r = Hash.new

	#### 補助クラスネームの追加処理
	if /\+/ =~ class_name
		class_add = "<span class='tagc'>#{class_name.sub( '+', '' )}</span> "
	else
		class_add = ''
	end

	puts 'Base food<br>' if @debug
	r = db.query( "SELECT * FROM #{$TB_FCT} WHERE FN='#{base_fn}';", false )
	base_energy = num_opt( r.first['ENERC_KCAL'], food_weight, frct_mode, @fct_frct['ENERC_KCAL'] )

	rr = db.query( "SELECT * FROM #{$TB_TAG} WHERE FN='#{base_fn}';", false )
	base_name = rr.first['name']
	base_tags = "<span class='tag1'>#{rr.first['tag1']}</span> <span class='tag2'>#{rr.first['tag2']}</span> <span class='tag3'>#{rr.first['tag3']}</span> <span class='tag4'>#{rr.first['tag4']}</span> <span class='tag5'>#{rr.first['tag5']}</span>"
 
	base_sub_components = "<td align='center'>#{food_weight.to_f}</td>"
	@fct_para.each do |e|
		t = num_opt( r.first[e], food_weight, frct_mode, @fct_frct[e] )
		base_sub_components << "<td align='center'>#{t}</td>"
	end


	r = db.query( "SELECT * FROM #{$TB_PARA} WHERE FN='#{base_fn}' AND JUTEN='#{juten}';", false )
	if r.first
		rr = db.query( "SELECT * FROM #{$TB_TAG} WHERE FN IN (#{r.first['para']});", false )
		rr.each do |e|
			food_no_list << e['FN']
			food_name_list << e['name']
			tag1_list << e['tag1']
			tag2_list << e['tag2']
			tag3_list << e['tag3']
			tag4_list << e['tag4']
			tag5_list << e['tag5']
		end
	end

	puts 'Display items<br>' if @debug
	juten_html = ''
	@fct_para.each do |e|
		juten_html << "<th>"
		juten_html << "<input class='form-check-input' type='radio' name='para_juten' id='para_#{e}' value='#{e}' onchange=\"cb_detail_para_juten('#{food_key}','#{food_weight}','#{base_fn}')\" #{$CHECK[ e == juten ]}>"
		juten_html << "</th>"
	end


	puts 'Display items<br>' if @debug
	fc_items_html = ''
	@fct_para.each do |e| fc_items_html << "<th align='right'>#{@fct_name[e]}</th>" end


	puts 'Food list<br>' if @debug
	food_html = "<tr class='fct_value_h'><td>#{base_fn}</td><td class='link_cursor'>#{class_add}#{base_name} #{base_tags}</td><td></td>#{base_sub_components}</tr>\n"


	c = 0
	r = db.query( "SELECT * FROM #{$TB_FCT} WHERE FN IN (#{r.first['para']});", false )
	r.each do |e|
		para_energy = num_opt( e['ENERC_KCAL'], food_weight, frct_mode, @fct_frct['ENERC_KCAL'] )
		para_weight = ( food_weight.to_f * base_energy / para_energy ).round( 1 )

		sub_components = "<td align='center'>#{para_weight}</td>"
		@fct_para.each do |ee|
			t = num_opt( e[ee], para_weight, frct_mode, @fct_frct[ee] )
			sub_components << "<td align='center'>#{t}</td>"
		end

		# 追加・変更ボタン
		add_button = "<span onclick=\"changingCB( '#{e['FN']}', '#{base_fn}', '#{para_weight}' )\">#{l['change']}</span>"

		tags = "<span class='tag1'>#{tag1_list[c]}</span> <span class='tag2'>#{tag2_list[c]}</span> <span class='tag3'>#{tag3_list[c]}</span> <span class='tag4'>#{tag4_list[c]}</span> <span class='tag5'>#{tag5_list[c]}</span>"
		food_html << "<tr class='fct_value'><td>#{food_no_list[c]}</td><td class='link_cursor' onclick=\"detailView( '#{food_no_list[c]}' )\">#{class_add}#{food_name_list[c]} #{tags}</td><td>#{add_button}</td>#{sub_components}</tr>\n"
		c += 1
	end

 
	return_button = ''
	return_button = "<div align='center' class='joystic_koyomi' onclick=\"returnCB( '', '' )\">#{l['signpost']}</div><br>" if base == 'cb'


	parallel_button = ''
	parallel_button = "<div align='center' class='joystic_active' onclick=\"cb_detail_sub( '#{food_key}', '#{food_weight}', '#{base_fn}' )\">#{l['parallel']}</div><br>" if base == 'cb'

	html = <<-"HTML"
	<div class='container-fluid'>
		<div class="row">
			<div class="col-11">#{return_button}</div>
			<div class="col-1">#{parallel_button}</div>
		</div>
		<div class="row">
  			<div class="col-3"><span class='h5'>#{food_name}</span></div>
  			<div class="col-3"><h5>#{food_weight.to_f} g</h5></div>
		</div>
	</div>
	<br>

	<table class="table table-sm table-hover">
		<thead>
			<tr>
	  			<th>#{l['juten']}</th>
	  			<th>#{@fct_name[juten]}</th>
				<th></th>
	  			<th></th>
				#{juten_html}
    		</tr>
			<tr>
	  			<th>#{l['fn']}</th>
	  			<th>#{l['name']}</th>
				<th></th>
	  			<th>#{l['weight']}</th>
				#{fc_items_html}
    		</tr>
  		</thead>

		#{food_html}
	</table>
HTML

end

puts html
