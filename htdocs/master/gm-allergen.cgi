#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser GM allergen editor 0.02b (2023/07/17)


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
		'allergen' 	=> "アレルゲン登録",\
		'fn' 		=> "食品番号",\
		'name' 		=> "食品名",\
		'class'		=> "表示区分",\
		'obligate'	=> "表示義務",\
		'recommend'	=> "表示推奨",\
		'user'		=> "ユーザー登録",\
		'others'	=> "ユーザー登録数",\
		'check'		=> "○",\
		'trash' 	=> "<img src='bootstrap-dist/icons/trash.svg' style='height:1.2em; width:1.2em;'>",\
		'regist'	=> "登　録"
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
allergen = @cgi['allergen'].to_i
allergen = 1 if allergen == 0
code = @cgi['code']
code.gsub!( /\s/, ',' ) unless code == ''
code.gsub!( '　', ',' ) unless code == ''
code.gsub!( '、', ',' ) unless code == ''
if @debug
	puts "command:#{command}<br>\n"
	puts "code:#{code}<br>\n"
	puts "allergen:#{allergen}<br>\n"
	puts "<hr>\n"
end

case command
when 'on'
	fn = code.split( ',' )
	fn.each do |e|
		if /P?\d\d\d\d\d/ =~ e
			db.query( "UPDATE #{$TB_EXT} SET allergen#{allergen}=1 WHERE FN='#{e}';", true )
		end
	end
when 'off'
	fn = code.split( ',' )
	fn.each do |e|
		if /P?\d\d\d\d\d/ =~ e
			db.query( "UPDATE #{$TB_EXT} SET allergen#{allergen}=0 WHERE FN='#{e}';", true )
		end
	end
end

food_name = ''
unless code == ''
	r = db.query( "SELECT name from #{$TB_TAG} WHERE FN='#{code}';", false )
	food_name = r.first['name'] if r.first
end

list_html = ''
query = ''
if allergen == 1 || allergen == 2
	query = "SELECT t1.*, t2.allergen#{allergen} FROM #{$TB_TAG} AS t1 INNER JOIN #{$TB_EXT} AS t2 ON t1.FN = t2.FN WHERE t2.allergen#{allergen}='1' ORDER BY t1.FN;"
else
	query = "SELECT t1.* FROM #{$TB_TAG} AS t1 INNER JOIN #{$TB_PAG} AS t2 ON t1.FN = t2.FN WHERE t2.user='#{user.name}' ORDER BY t1.FN;"
end
r = db.query( query, false )
r.each do |e|
	list_html << "<tr>"
	list_html << "<td>#{e['FN']}</td>"
	list_html << "<td>#{e['name']} #{e['tag1']} #{e['tag2']} #{e['tag3']} #{e['tag4']} #{e['tag5']}</td>"

	r = db.query( "SELECT COUNT(FN) FROM #{$TB_PAG} WHERE FN='#{e['FN']}';", false )
	count = r.first['COUNT(FN)']

	list_html << "<td>#{count}</td>"
	if allergen == 1 || allergen == 2
		list_html << "<td><span onclick=\"offAllergen( '#{e['FN']}' )\">#{l['trash']}</span></td>"
	else
		list_html << "<td></td>"
	end
	list_html << '</tr>'
end

list_html << '<tr><td>no item listed.</td></tr>' if list_html == ''

select_a1 = ['', 'SELECTED', '', '']
select_a2 = ['', '', 'SELECTED', '']
select_a3 = ['', '', '', 'SELECTED']

regist_button = ''
regist_button = "<button class='btn btn-sm btn-info' type='button' onclick=\"onAllergen()\">#{l['regist']}</button>" unless allergen == 3

html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l['allergen']}: #{food_name}</h5></div>
	</div>
	<div class='row'>
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<label class="input-group-text">#{l['class']}</label>
				<select class='form-select form-select-sm' id='allergen' onchange='changeAllergen()'>
					<option value='1' #{select_a1[allergen]}>#{l['obligate']}</option>
					<option value='2' #{select_a2[allergen]}>#{l['recommend']}</option>
					<option value='3' #{select_a3[allergen]}>#{l['user']}</option>
				</select>
			</div>
		</div>
		<div class='col-9'>
			<div class="input-group input-group-sm">
				<label class="input-group-text">#{l['fn']}</label>
				<input type="text" class="form-control" id="code" value="#{code}">
			</div>
		</div>
	</div>
	<br>

	<div class='row'>
		#{regist_button}
	</div>
	<br>

	<table class='table table-sm table-striped'>
		<thead>
			<td width='10%'>#{l['fn']}</td>
			<td width='20%'>#{l['name']}</td>
			<td width='10%'>#{l['others']}</td>
			<td width='10%'></td>
		</thead>

		#{list_html}
	</table>
HTML

puts html
