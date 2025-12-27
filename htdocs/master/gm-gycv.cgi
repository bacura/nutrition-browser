#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser GM yellow green color vegetable editor 0.02b (2023/07/16)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
#script = File.basename( $0, '.cgi' )

#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		'food_no' 	=> "食品番号",\
		'regist' 	=> "登録",\
		'gycv_edit' => "緑黄色野菜エディタ"
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

#### GM check
if user.status < 8
	puts "GM error."
	exit
end


#### POST
command = @cgi['command']
food_no = @cgi['food_no']
if @debug
	puts "command:#{command}<br>\n"
	puts "food_no:#{food_no}<br>\n"
	puts "<hr>\n"
end

case command
when 'on'
	db.query( "UPDATE #{$TB_EXT} SET gycv='1' WHERE FN='#{food_no}';", true )
when 'off'
	db.query( "UPDATE #{$TB_EXT} SET gycv ='0' WHERE FN='#{food_no}';", true )
end

list_html = ''
food_no_list = []

r = db.query( "SELECT * from #{$TB_TAG} WHERE FN IN ( SELECT FN FROM #{$TB_EXT} WHERE gycv ='1' ORDER BY FN ASC );", false )
r.each do |e|
	list_html << "<div class='row'>"
	list_html << "<div class='col-1'><button class='btn btn-sm btn-outline-danger' type='button' onclick=\"offGYCV( '#{e['FN']}' )\">x</button></div>"
	list_html << "<div class='col-2'>#{e['FN']}</div>"
	list_html << "<div class='col-4'>#{e['name']}・#{e['tag1']} #{e['tag2']} #{e['tag3']} #{e['tag4']} #{e['tag5']}</div>"
	list_html << '</div>'
end

list_html = 'no item listed.' if r.size == 0

puts "HTML<br>" if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l['gycv_edit']}: </h5></div>
	</div>
	<div class='row'>
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="weight">#{l['food_no']}</label>
				<input type="text" maxlength="5" class="form-control" id="food_no" value="#{food_no}" onchange="onGYCV()">
				<button class="btn btn-outline-primary" type="button" onclick="onGYCV()">#{l['regist']}</button>
			</div>
		</div>
	</div>
	<br>
	<hr>
	#{list_html}
HTML

puts html
