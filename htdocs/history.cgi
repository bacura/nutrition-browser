#! /usr/bin/ruby
#encoding: utf-8
#Nutritoin browser history 0.2.8 (2025/12/18)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

$ALL_LIMIT = 100

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
		history:	"履歴",
		all:	 "全部",
		special:	"特殊",
		login:	"ログインしてください",
		recipe:	"レシピ",
		fno:	"食品番号",
		wvegi:	"野菜類（白色）",
		gyvegi:	"野菜類（緑黄色）",
		sg1:	"穀",
		sg2:	"芋",
		sg3:	"甘",
		sg4:	"豆",
		sg5:	"種",
		sg6:	"菜",
		sg7:	"果",
		sg8:	"茸",
		sg9:	"藻",
		sg10:	"魚",
		sg11:	"肉",
		sg12:	"卵",
		sg13:	"乳",
		sg14:	"油",
		sg15:	"菓",
		sg16:	"飲",
		sg17:	"調",
		sg18:	"流",
		sg0:	"特",
		sgr:	"レ",
		cboard:	"<img src='bootstrap-dist/icons/card-text.svg' style='height:1.2em; width:1.2em;'>",
		printer:	"<img src='bootstrap-dist/icons/printer.svg' style='height:1.2em; width:1.2em;'>",
		cp2words:	"<img src='bootstrap-dist/icons/eyedropper.svg' style='height:1.2em; width:1.2em;'>",
		calendar:	"<img src='bootstrap-dist/icons/calendar-plus.svg' style='height:1.2em; width:1.2em;'>"
	}

	return l[language]
end

#### Getting history
def get_histry( db, l, sub_fg )
	history = []
	sgh = Hash.new
	res = db.query( "SELECT his FROM #{$TB_HIS} WHERE user=?", false, [db.user.name] )&.first
	t = res['his'].split( "\t" )

	gycv = sub_fg == '6_'
	sub_fg = '6' if gycv

	if sub_fg == 'all'
		history = t.first( $ALL_LIMIT )
		t.each do |entry|
			sgh[entry] = entry.include?( '-r-' ) ? 'r' : 'f'
		end
	else

		t.each do |entry|
			next unless ( /[UPC]/ =~ entry && entry[1..2].to_i == sub_fg.to_i ) || entry[0..1].to_i == sub_fg.to_i || entry.include?( '-r-' )
			sgh[entry] = entry.include?( '-r-' ) ? 'r' : 'f'
			history << entry
		end
	end

	html = ''
	history.each do |entry|
		if sgh[entry] == 'f' && sub_fg != 'R'
			res_tag = db.query( "SELECT * FROM #{$TB_TAG} WHERE FN=?", false, [entry] )&.first
			next unless res_tag

			if sub_fg == '6'
				res2 = db.query( "SELECT gycv FROM #{$TB_EXT} WHERE FN=?", false, [entry] )&.first
				next if res2 && ( res2['gycv'] == 1 && !gycv ) || ( res2['gycv'] != 1 && gycv )
			end
			food_name = res_tag['name']
			tags = tagnames( res_tag )

			add_button = "<span onclick=\"addingCB( '#{entry}', '', '#{food_name}' )\">#{l[:cboard]}</span>" if db.user.name
			koyomi_button = "<span onclick=\"addKoyomi( '#{entry}' )\">#{l[:calendar]}</span>" if db.user.status >= 2

			html += "<tr class='fct_value'><td class='link_cursor' onclick=\"detailView_his( '#{entry}' )\">#{tags}</td><td>#{add_button}&nbsp;#{koyomi_button}</td></tr>\n"
		elsif sgh[entry] == 'r' && ( sub_fg == 'R' || sub_fg == 'all' )
			recipe_res = db.query( "SELECT * FROM #{$TB_RECIPE} WHERE code=?", false, [entry] )&.first
			next unless recipe_res

			recipe_name = recipe_res['name']
			koyomi_button = "<span onclick=\"addKoyomi( '#{entry}' )\">#{l[:calendar]}</span>" if db.user.status >= 2
			print_button = "<span onclick=\"print_templateSelect( '#{entry}' )\">#{l[:printer]}</span>"
			cp2w_button = "<span onclick=\"cp2words( '#{entry}', '' )\">#{l[:cp2words]}</span>"

			html += "<tr class='fct_value'><td class='link_cursor' onclick=\"initCB( 'load', '#{entry}', '#{recipe_res['user']}' )\">#{recipe_name}</td><td>#{add_button}&nbsp;#{koyomi_button}&nbsp;#{print_button}&nbsp;#{cp2w_button}</td></tr>\n"
		end
	end

	return html
end

#### Sub group HTML
def sub_menu( l )
	html_sub = <<-"HTML_SUB"
<span class="btn badge rounded-pill bg-info text-dark" onclick="historySub( '1' )">#{l[:sg1]}</span>
<span class="btn badge rounded-pill bg-info text-dark" onclick="historySub( '2' )">#{l[:sg2]}</span>
<span class="btn badge rounded-pill bg-info text-dark" onclick="historySub( '3' )">#{l[:sg3]}</span>
<span class="btn badge rounded-pill bg-danger" onclick="historySub( '4' )">#{l[:sg4]}</span>
<span class="btn badge rounded-pill bg-warning text-dark" onclick="historySub( '5' )">#{l[:sg5]}</span>
<span class="btn badge rounded-pill bg-light text-success" onclick="historySub( '6' )">#{l[:sg6]}</span>
<span class="btn badge rounded-pill bg-success" onclick="historySub( '6_' )">#{l[:sg6]}</span>
<span class="btn badge rounded-pill bg-info text-dark" onclick="historySub( '7' )">#{l[:sg7]}</span>
<span class="btn badge rounded-pill bg-success" onclick="historySub( '8' )">#{l[:sg8]}</span>
<span class="btn badge rounded-pill bg-success" onclick="historySub( '9' )">#{l[:sg9]}</span>
<span class="btn badge rounded-pill bg-danger" onclick="historySub( '10' )">#{l[:sg10]}</span>
<span class="btn badge rounded-pill bg-danger" onclick="historySub( '11' )">#{l[:sg11]}</span>
<span class="btn badge rounded-pill bg-danger" onclick="historySub( '12' )">#{l[:sg12]}</span>
<span class="btn badge rounded-pill bg-light text-dark" onclick="historySub( '13' )">#{l[:sg13]}</span>
<span class="btn badge rounded-pill bg-warning text-dark" onclick="historySub( '14' )">#{l[:sg14]}</span>
<span class="btn badge rounded-pill bg-secondary" onclick="historySub( '15' )">#{l[:sg15]}</span>
<span class="btn badge rounded-pill bg-primary" onclick="historySub( '16' )">#{l[:sg16]}</span>
<span class="btn badge rounded-pill bg-light text-dark" onclick="historySub( '17' )">#{l[:sg17]}</span>
<span class="btn badge rounded-pill bg-secondary" onclick="historySub( '18' )">#{l[:sg18]}</span>
<span class="btn badge rounded-pill bg-light text-dark" onclick="historySub( '00' )">#{l[:sg0]}</span>
<span class="btn badge rounded-pill bg-dark text-light" onclick="historySub( 'R' )">#{l[:sgr]}</span>
HTML_SUB
	puts html_sub
	exit
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
history = Hash.new
db = Db.new( user, @debug, false )

puts 'POST<br>' if @debug
command = @cgi['command'].empty? ? 'init' : @cgi['command']
sub_fg = @cgi['sub_fg']
if @debug
	puts "command: #{command}<br>"
	puts "sub_fg: #{sub_fg}<br>"
	puts "<hr>"
end


#### Sub group menu
case command
when 'menu'
	sub_menu( l )

when 'sub'

when 'modal_body'
	code = @cgi['code']
	if /\-r\-/ =~ code
		table_content = "<td align='center' onclick=\"addKoyomi( '#{recipe.code}' )\">#{l[:calendar]}<br><br>#{l[:koyomi]}</td>"
		table_content << "<td align='center' onclick=\"cp2words( '#{recipe.code}', '' )\">#{l[:cp2words]}<br><br>#{l[:pick]}</td>"
	else
		table_content = "<td align='center' onclick=\"addKoyomi( '#{recipe.code}' )\">#{l[:calendar]}<br><br>#{l[:koyomi]}</td>"
	end
	puts "<table class='table table-borderless'><tr>#{table_content}</tr></table>"

	exit

when 'modal_label'
    puts @cgi['code']

	exit

else
	puts "LOAD config<br>" if @debug

	sub_fg = 1
	res = db.query( "SELECT history FROM #{$TB_CFG} WHERE user='#{user.name}';", false )&.first
	if res
		unless res['history'].to_s.empty?
			history = JSON.parse( res['history'] )
			sub_fg = history['sub_fg'] if history['sub_fg']
		end
	end
end


puts 'Group name<br>' if @debug
sub_title = case sub_fg
	when '00' then "#{l[:special]}"
	when '6'  then "#{l[:wvegi]}"
	when '6_' then "#{l[:gyvegi]}"
	when 'R'  then "#{l[:recipe]}"
	else @category[sub_fg.to_i]
end


puts 'History Line All<br>' if @debug
food_html_all = get_histry( db, l, 'all' )


puts 'History Line SG<br>' if @debug
food_html_sg = get_histry( db, l, sub_fg )


puts 'HTML<br>' if @debug
html = <<~"HTML"
<div class='container-fluid'>
	<div class="row">
		<div class="col">
			<h5>#{l[:history]}: #{l[:all]}</h5>
			<table class="table table-sm table-hover">
				#{food_html_all}
			</table>
		</div>
		<div class="col">
			<h5>#{l[:history]}: #{sub_title}</h5>
			<table class="table table-sm table-hover">
				#{food_html_sg}
			</table>
		</div>
	</div>
</div>
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================
#Update config
history['sub_fg'] = sub_fg
unless history['sub_fg'].to_s.empty?
	history_ = JSON.generate( history )
	db.query( "UPDATE #{$TB_CFG} SET history=? WHERE user=?", false, [history_, user.name] ) unless user.status == $ASTRAL
end

#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'

	js = <<~JS
<script type='text/javascript'>
	var historySub = ( sub_fg ) => {
		postLayer( '#{myself}', 'sub', true, 'L1', {sub_fg});
	};
</script>
JS

	puts js

end

puts '(^q^)' if @debug