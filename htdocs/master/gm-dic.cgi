#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser GM food alias dictionary editor 0.5.2 (2025/04/26)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

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
	l['jp'] = {
		fg: "食品群",
		fn: "食品",
		alias: "別名",
		linkno: "指定食品番号",
		fg00: "特・その他",
		fg01: "穀",
		fg02: "芋",
		fg03: "甘",
		fg04: "豆",
		fg05: "種",
		fg06: "菜",
		fg07: "果",
		fg08: "茸",
		fg09: "藻",
		fg10: "魚",
		fg11: "肉",
		fg12: "卵",
		fg13: "乳",
		fg14: "油",
		fg15: "菓",
		fg16: "飲",
		fg17: "調",
		fg18: "調",
		eraser: "<img src='bootstrap-dist/icons/eraser.svg' style='height:1.8em; width:1.8em;'>",
		add: "追　加"
	}

	return l[language]
end

def generate_category_menu( l )
	html_sub = <<-"HTML_SUB"
<span class="badge rounded-pill bg-info text-dark" id="category1" onclick="changeDic( '01' )">#{l[:fg01]}</span>
<span class="badge rounded-pill bg-info text-dark" id="category2" onclick="changeDic( '02' )">#{l[:fg02]}</span>
<span class="badge rounded-pill bg-info text-dark" id="category3" onclick="changeDic( '03' )">#{l[:fg03]}</span>
<span class="badge rounded-pill bg-danger" id="category4" onclick="changeDic( '04' )">#{l[:fg04]}</span>
<span class="badge rounded-pill bg-warning text-dark" id="category5" onclick="changeDic( '05' )">#{l[:fg05]}</span>
<span class="badge rounded-pill bg-success" id="category6" onclick="changeDic( '06' )">#{l[:fg06]}</span>
<span class="badge rounded-pill bg-info text-dark" id="category7" onclick="changeDic( '07' )">#{l[:fg07]}</span>
<span class="badge rounded-pill bg-success" id="category8" onclick="changeDic( '08' )">#{l[:fg08]}</span>
<span class="badge rounded-pill bg-success" id="category9" onclick="changeDic( '09' )">#{l[:fg09]}</span>
<span class="badge rounded-pill bg-danger" id="category10" onclick="changeDic( '10' )">#{l[:fg10]}</span>
<span class="badge rounded-pill bg-danger" id="category11" onclick="changeDic( '11' )">#{l[:fg11]}</span>
<span class="badge rounded-pill bg-danger" id="category12" onclick="changeDic( '12' )">#{l[:fg12]}</span>
<span class="badge rounded-pill bg-light text-dark" id="category13" onclick="changeDic( '13' )">#{l[:fg13]}</span>
<span class="badge rounded-pill bg-warning text-dark" id="category14" onclick="changeDic( '14' )">#{l[:fg14]}</span>
<span class="badge rounded-pill bg-secondary" id="category15" onclick="changeDic( '15' )">#{l[:fg15]}</span>
<span class="badge rounded-pill bg-primary" id="category16" onclick="changeDic( '16' )">#{l[:fg16]}</span>
<span class="badge rounded-pill bg-light text-dark" id="category17" onclick="changeDic( '17' )">#{l[:fg17]}</span>
<span class="badge rounded-pill bg-secondary" id="category18" onclick="changeDic( '18' )">#{l[:fg18]}</span>
<span class="badge rounded-pill bg-light text-dark" id="category0" onclick="changeDic( '00' )">#{l[:fg00]}</span>
HTML_SUB
	return html_sub
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
sg = @cgi['sg']
sg = '01' if command == 'init'
org_name = CGI.escapeHTML( @cgi['org_name'].to_s )
org_name_def = CGI.escapeHTML( @cgi['org_name_def'].to_s )
aliases = CGI.escapeHTML( @cgi['aliases'].to_s )
dfn = CGI.escapeHTML( @cgi['dfn'].to_s )
if @debug
	puts "command:#{command}<br>\n"
	puts "sg:#{sg}<br>\n"
	puts "org_name:#{org_name}<br>\n"
	puts "org_name_def:#{org_name_def}<br>\n"
	puts "aliases:#{aliases}<br>\n"
	puts "dfn:#{dfn}<br>\n"
	puts "<hr>\n"
end

case command
when 'menu'
	puts generate_category_menu( l )
	exit

when 'new'
	unless aliases.empty?
		aliases_list = aliases.split(/[\s、，,]+/).uniq
		aliases_list.each do |e|

			r = db.query( "SELECT * FROM #{$MYSQL_TB_DIC} WHERE alias='#{e}' AND org_name='#{org_name}' AND FG ='#{sg}';", false )
			db.query( "INSERT INTO #{$MYSQL_TB_DIC} SET alias='#{e}', org_name='#{org_name}', def_fn='#{dfn}', FG ='#{sg}', user='#{user.name}';", true ) unless r.first
		end
	end

when 'update'
	org_name = org_name_def.split( '_' ).first
  	unless org_name.empty?
		db.query( "DELETE FROM #{$MYSQL_TB_DIC} WHERE org_name='#{org_name}' AND FG ='#{sg}' AND ( def_fn='#{dfn}' OR def_fn='' OR def_fn IS NULL);", true )
		unless aliases.empty?
			aliases_list = aliases.split(/[\s、，,]+/).uniq
			aliases_list.each do |e|
				db.query( "INSERT INTO #{$MYSQL_TB_DIC} SET alias='#{e}', org_name='#{org_name}', def_fn='#{dfn}', FG ='#{sg}', user='#{user.name}';", true )
			end
		end

	end
end

puts "Make aliases list HTML" if @debug
list_html = "<div class='row'>"
list_html << "<div class='col-3 cb_header'>#{l[:fn]}</div>"
list_html << "<div class='col-1 cb_header'>#{l[:linkno]}</div>"
list_html << "<div class='col-8 cb_header'>#{l[:alias]}</div>"
list_html << '</div>'

r = db.query( "SELECT DISTINCT org_name, def_fn FROM #{$MYSQL_TB_DIC} WHERE FG ='#{sg}' ORDER BY org_name ASC;", false )
r.each do |e|
	alias_value = ''
	def_fn = ''
	tags = ''
	rr = db.query( "SELECT DISTINCT * from #{$MYSQL_TB_DIC} WHERE org_name='#{e['org_name']}' AND FG ='#{sg}' AND ( def_fn='#{e['def_fn']}' OR def_fn='' OR def_fn IS NULL);", false )
	rr.each do |ee|
		alias_value << "#{ee['alias']},"
		def_fn = ee['def_fn']
		tags = ''
		unless def_fn.empty?
			rrr = db.query( "SELECT * FROM #{$MYSQL_TB_TAG} WHERE FN='#{def_fn}';", false )
			tags = bind_tags( rrr ) if rrr.first
		end
	end
	alias_value.chop!
	food = tags.empty? ? e['org_name'] : tags

	list_html << "<div class='row'>"
	list_html << "<div class='col-3'>#{food}</div>"
	list_html << "<div class='col-1'><input type='text' class='form-control form-control-sm' id=\"dfn_#{e['org_name']}_#{e['def_fn']}\" value='#{def_fn}' onchange=\"saveDic( '#{e['org_name']}_#{e['def_fn']}', '#{sg}' )\"></div>"
	list_html << "<div class='col-8'><input type='text' class='form-control form-control-sm' id=\"#{e['org_name']}_#{e['def_fn']}\" value='#{alias_value}' onchange=\"saveDic( '#{e['org_name']}_#{e['def_fn']}', '#{sg}' )\"></div>"
	list_html << '</div>'
end

puts "Make food sub group select list" if @debug
select_html = "<select id='new_fg' class='form-control'>"
1.upto( 18 ) do |c|
	select_html << "<option value='#{@fg[c]}' #{$SELECT[@fg[c] == sg]}>#{@category[c]}</option>"
end
select_html << "<option value='00'>#{@category[0]}</option>"
select_html << '</select>'

puts "HTML" if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-2'>
			<div class="input-group input-group-sm">
				<span class="input-group-text">#{l[:fg]}</span>
				#{select_html}
			</div>
		</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-2'>
			<div class="input-group input-group-sm">
				<span class="input-group-text">#{l[:fn]}</span>
				<input type='text' id='new_org_name' value='#{org_name}' class='form-control'>
			</div>
		</div>
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<span class="input-group-text">#{l[:linkno]}</span>
				<input type='text' id='dic_def_fn' value='#{dfn}' class='form-control'>
			</div>
		</div>
		<div class='col-7'>
			<div class="input-group input-group-sm">
				<span class="input-group-text">#{l[:alias]}</span>
				<input type='text' id='new_alias' class='form-control'>
			</div>
		</div>
	</div>
	<br>

	<div class='row'><button type='button' class='btn btn-outline-primary btn-sm btn-sm' onclick="newDic()">#{l[:add]}</button></div>
	<br>

	#{list_html}
HTML

puts html

#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init' || command == 'direct'
js = <<-"JS"
<script type='text/javascript'>

// Food name dictionary Sub group
var changeDic = ( sg ) => {
    postLayer( 'master/#{myself}', 'change', true, 'L1',
    	{ sg }
	);
};

// Direct food name dictionary button
var saveDic = ( org_name_def, sg ) => {
	const aliases = document.getElementById( org_name_def ).value;
	const dfn = document.getElementById( 'dfn_' + org_name_def ).value;
	postLayer( 'master/#{myself}', 'update', true, 'L1',
		{ org_name_def, aliases, sg, dfn }
	);
	displayREC();
};

// Add new food into dictionary button
var newDic = () => {
	const org_name = document.getElementById( 'new_org_name' ).value;
	const aliases = document.getElementById( 'new_alias' ).value;
	const sg = document.getElementById( 'new_fg' ).value;
	const dfn = document.getElementById( 'dic_def_fn' ).value;
	postLayer( 'master/#{myself}', 'new', true, 'L1',
		{ org_name, aliases, sg, dfn }
	);
	displayREC();
};	

</script>

JS

	puts js
end
