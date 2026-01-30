#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 GM Shun editor 0.0.3 (2026/01/29)


#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )
shun_m = %w( jan feb mar apr may jun jul aug sep oct nov dec )
shun_ms = [:jan, :feb, :mar, :apr, :may, :jun, :jul, :aug, :sep, :oct, :nov, :dec ]

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		food_no:"食品番号",
		food_name:"食品名",
		save: "保　存",
		delete: "削　除",
		jan: "１月",
		feb: "２月",
		mar: "３月",
		apr: "４月",
		may: "５月",
		jun: "６月",
		jul: "７月",
		aug: "８月",
		sep: "９月",
		oct: "１０月",
		nov: "１１月",
		dec: "１２月",
		squere: "■",
		err_user: "ユーザー食品に旬の設定はできません。",
		shun_edit: "旬エディタ"
	}

	return l[language]
end


def shun_list( table_head_td, db, l )
	food_tr_html = ''
	res = db.query( "SELECT ext.FN AS FN, tag.name AS name, tag.class1 AS class1, tag.class2 AS class2, tag.class3 AS class3, tag.tag1 AS tag1, tag.tag2 AS tag2, tag.tag3 AS tag3, tag.tag4 AS tag4, tag.tag5 AS tag5, LPAD( BIN( ext.shun ), 12, '0' ) AS shun_bit from #{$TB_EXT} AS ext INNER JOIN #{$TB_TAG} AS tag ON ext.FN=tag.FN WHERE ext.shun <> 0;", false )
	res.each do |e|
		food_tr_html << "<tr onclick=\"editShun( '#{e['FN']}', '0' )\">"
		food_tr_html << "<td>#{e['FN']}</td>"
		food_tr_html << "<td>#{tagnames( e )}</td>"

		12.times do |posi|
			t = e['shun_bit'][posi] == '1' ? "<td align='center'>#{l[:squere]}</td>" : '<td></td>'
			food_tr_html << t
		end
		food_tr_html << '</tr>'
	end

	html = <<~HTML
	<div class='container-fluid'>
		<div class='row'>
			<div class='col'><h5>#{l[:shun_edit]}:</h5></div>
			<table class='table table-sm table-hover'>
				<tr>
					<td>#{l[:food_no]}</td>
					<td>#{l[:food_name]}</td>
					#{table_head_td}
				</tr>

				#{food_tr_html}
			</table>
		</div>
	</div>
HTML

	puts html

end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )
shun =Array.new

#### GM check
if user.status < 8
	puts "GM error."
#	exit
end


#### POSTデータの取得
command = @cgi['command']
food_no = @cgi['food_no'].to_s
direct = @cgi['direct'].to_i
12.times do |i| shun[i] = @cgi[shun_m[i]].to_i end

if @debug
	puts "command:#{command}<br>\n"
	puts "food_no:#{food_no}<br>\n"
	puts "direct:#{direct}<br>\n"
end

table_head_td = ''
12.times do |i| table_head_td << "<td width='5%' align='center'>#{l[shun_ms[i]]}</td>" end 


case command
when 'editor'
	if /[PCU]/ =~ food_no
		puts l[:err_user]
		exit
	end 

	food_name = ''
	res = db.query( "SELECT tag.name AS name, tag.class1 AS class1, tag.class2 AS class2, tag.class3 AS class3, tag.tag1 AS tag1, tag.tag2 AS tag2, tag.tag3 AS tag3, tag.tag4 AS tag4, tag.tag5 AS tag5, LPAD( BIN( ext.shun ), 12, '0' ) AS shun_bit from #{$TB_EXT} AS ext INNER JOIN #{$TB_TAG} AS tag ON ext.FN=tag.FN WHERE ext.FN=?", false, [food_no] )&.first
	if res
		food_name = tagnames( res )
		shun_bit = res['shun_bit']
	else
		food_name = ''
		shun_bit = '000000000000'
	end

	table_edit_td = ''
	12.times do |i|
		table_edit_td << "<td align='center'><input type='checkbox' id='#{shun_m[i]}' class='form-check-input' #{$CHECK[shun_bit[i] == '1']}></td>"
	end 

	html = <<~HTML
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l[:shun_edit]}:</h5></div>

		<table class='table table-sm table-hover'>
			<tr>
				<td>#{l[:food_no]}</td>
				<td>#{l[:food_name]}</td>
				#{table_head_td}
			</tr>

			<tr>
				<td>#{food_no}</td>
				<td>#{food_name}</td>
				#{table_edit_td}
			</tr>
		</table>
	</div>
	<br>

	<div class='row'>
		<div class='col-11'>
			<div class='row'>
				<button class='btn btn-primary btn-sm' type='button' onclick='saveShun( \"#{food_no}\", \"#{direct}\" )'>#{l[:save]}</button>
			</div>
		</div>
		<div class='col-1'>
			<button class='btn btn-danger btn-sm' type='button' onclick='deleteShun( \"#{food_no}\", \"#{direct}\" )'>#{l[:delete]}</button>
		</div>
	</div>
</div>

HTML

	puts html

when 'save'
	shun_bit = shun.join( '' )
	shun_bit = '000000000000' unless shun_bit.size == 12
	db.query( "UPDATE #{$TB_EXT} SET shun=b'#{shun_bit}' WHERE FN=?", true, [food_no] )
	shun_list( table_head_td, db, l )

when 'delete'
	shun_bit = '000000000000'
	db.query( "UPDATE #{$TB_EXT} SET shun=b'#{shun_bit}' WHERE FN=?", true, [food_no] )
	shun_list( table_head_td, db, l )

else
	shun_list( table_head_td, db, l )

end


#==============================================================================
# POST PROCESS
#==============================================================================


#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init' || direct == 1
	js = <<-"JS"
<script type='text/javascript'>



// Editor
var editShun = ( food_no, direct ) => {
	postLayer( mp + '#{myself}', 'editor', true, 'LF', { food_no, direct });
};

// Shun OFF
var saveShun = ( food_no, direct ) => {
	const jan = document.getElementById( 'jan' ).checked ? 1 : 0;
	const feb = document.getElementById( 'feb' ).checked ? 1 : 0;
	const mar = document.getElementById( 'mar' ).checked ? 1 : 0;
	const apr = document.getElementById( 'apr' ).checked ? 1 : 0;
	const may = document.getElementById( 'may' ).checked ? 1 : 0;
	const jun = document.getElementById( 'jun' ).checked ? 1 : 0;
	const jul = document.getElementById( 'jul' ).checked ? 1 : 0;
	const aug = document.getElementById( 'aug' ).checked ? 1 : 0;
	const sep = document.getElementById( 'sep' ).checked ? 1 : 0;
	const oct = document.getElementById( 'oct' ).checked ? 1 : 0;
	const nov = document.getElementById( 'nov' ).checked ? 1 : 0;
	const dec = document.getElementById( 'dec' ).checked ? 1 : 0;

	postLayer( mp + '#{myself}', 'save', true, 'LF', { food_no, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec });
	if( direct==1 ){
		dlf = false;
		displayBW();
	}
	displayREC();
};

// Editor
var deleteShun = ( food_no, direct ) => {
	postLayer( mp + '#{myself}', 'delete', true, 'LF', { food_no });
	displayREC();
};

</script>
JS

end

puts js
puts '(^q^)' if @debug
