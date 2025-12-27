#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser GM unit editor 0.12b (2023/07/17)

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
		'load' 	=> "読み込み",\
		'notte' 	=> "注釈",\
		'save' 	=> "保存",\
		'all' 	=> "網羅的単位変換",\
		'from' 	=> "変換元",\
		'to' 	=> "変換先",\
		'arrow' 	=> "→",\
		'exe' 	=> "変換実行",\
		'unit' 	=> "単位",\
		'value'	=> "値",\
		'unit_edit' => "単位エディタ"
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


#### Getting POST
command = @cgi['command']
code = @cgi['code']
code = '' if code == nil
code.gsub!( /\s/, ',' )
code.gsub!( '　', ',' )
code.gsub!( '、', ',' )
bunit = @cgi['bunit']
aunit = @cgi['aunit']
if @debug
	puts "command:#{command}<br>\n"
	puts "code:#{code}<br>\n"

end

unith = Hash.new

case command
when 'update'
	0.upto( 9 ) do |c|
		if @cgi["uk#{c}"] != '' && @cgi["uk#{c}"] != nil
			if @cgi["uv#{c}"] != '' && @cgi["uv#{c}"] != nil
				unith[@cgi["uk#{c}"]] = @cgi["uv#{c}"].to_f
			else
				unith[@cgi["uk#{c}"]] = 0.0
			end
		end
	end
	unith['note'] = @cgi['note']

	unit = JSON.generate( unith )
	fn = code.split( ',' )
	fn.each do |e|
		db.query( "UPDATE #{$TB_EXT} SET unit='#{unit}' WHERE FN='#{e}';", true ) if /\d\d\d\d\d/ =~ e || /P\d\d\d\d\d/ =~ e
	end
when 'exunit'
	res = db.query( "SELECT * FROM recipe;", false )
	res.each do |r|
		ex_flag = false
		if r['sum'] != '' && r['sum'] != nil
			sum_list = []
			food_list = r['sum'].split( "\t" )
			food_list.each do |e|
				a = e.split( ':' )
				if a[2] == bunit && code == a[0]
					a[2] = aunit
					ex_flag = true
				end
				sum_list << a.join( ':' )
			end

			if ex_flag
				sum_new = sum_list.join( "\t" )
				db.query( "UPDATE recipe SET sum='#{sum_new}' WHERE user='#{r['user']}' AND code='#{r['code']}';", true )
			end
		end
	end

	res = db.query( "SELECT * FROM koyomi;", false )
	res.each do |r|
		ex_flag = false
		if r['koyomi'] != '' && r['koyomi'] != nil && r['tdiv'] != 4
			koyomi_list = []
			food_list = r['koyomi'].split( "\t" )
			food_list.each do |e|
				a = e.split( '~' )
				if a[2] == bunit && code == a[0]
					a[2] = aunit
					ex_flag = true
				end
				koyomi_list << a.join( '~' )
			end

			if ex_flag
				koyomi_new = koyomi_list.join( "\t" )
				db.query( "UPDATE koyomi SET koyomi='#{koyomi_new}' WHERE user='#{r['user']}' AND tdiv='#{r['tdiv']}' AND date='#{r['date']}';", true )
			end
		end
	end
end

uk_set = []
uv_set = []
note = ''
unless code == ''
	puts 'Loading unit JSON<br>' if @debug
	r = db.query( "SELECT name from #{$TB_TAG} WHERE FN='#{code}';", false )
	food_name = r.first['name']

	r = db.query( "SELECT unit from #{$TB_EXT} WHERE FN='#{code}';", false )
	if r.first
		if r.first['unit'] != nil && r.first['unit'] != ''
			unitj = JSON.parse( r.first['unit'] )
			unitj.each do |k, v|
				if k == 'note'
					note = v
				else
					uk_set << k
					uv_set << v
				end
			end
		end
	end
end


puts 'Unit HTML<br>' if @debug
unit_html = ''
0.upto( 4 ) do |c|
	unit_html << "<div class='row'>"
	unit_html << "<div class='col' align='right'><input type='text' class='form-control form-control-sm' id='uk#{c * 2}' value='#{uk_set[c * 2]}'></div>"
	unit_html << "<div class='col' align='right'><input type='number' class='form-control form-control-sm' id='uv#{c * 2}' value='#{uv_set[c * 2]}'></div>"
	unit_html << "<div class='col-1'></div>"
	unit_html << "<div class='col' align='right'><input type='text' class='form-control form-control-sm' id='uk#{c * 2 + 1}' value='#{uk_set[c * 2 + 1]}'></div>"
	unit_html << "<div class='col' align='right'><input type='number' class='form-control form-control-sm' id='uv#{c * 2 + 1}' value='#{uv_set[c * 2 + 1]}'></div>"
	unit_html << "</div>"
	unit_html << "<br>"
end


puts 'HTML<br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l['unit_edit']}: #{food_name}</h5></div>
	</div><br>

	<div class='row'>
		<div class='col-6'>
			<div class='input-group input-group-sm'>
				<label class="input-group-text">#{l['food_no']}</label>
  				<input type="text" class="form-control" id="food_no" value="#{code}">
				<button class='btn btn-sm btn-outline-primary' type='button' onclick=\"initUnit()\">#{l['load']}</button>
			</div>
		</div>
	</div><br>

	<div class='row'>
		<div class='col' align='center'>#{l['unit']}</div>
		<div class='col' align='center'>#{l['value']}</div>
		<div class='col-1'></div>
		<div class='col' align='center'>#{l['unit']}</div>
		<div class='col' align='center'>#{l['value']}</div>
	</div>
	#{unit_html}
	<br>

	<div class='row'>
		<div class='col-1'>#{l['note']}</div>
	</div>
	<div class='row'>
		<div class='col-10'><input type='text' class='form-control form-control-sm' id='note' value='#{note}'></div>
		<div class='col-1'></div>
		<div class='col' align='center'><button class='btn btn-sm btn-outline-danger' type='button' onclick="updateUint()">#{l['save']}</button></div>
	</div>
	<br>

</div>
<hr>

<div class='row'>
	<div class='col'>#{l['all']}</div>
	<div class='col'><input type='text' class='form-control form-control-sm' id='bunit' value='' placeholder='#{l['from']}'></div>
	<div class='col' align="center">#{l['arrow']}</div>
	<div class='col'><input type='text' class='form-control form-control-sm' id='aunit' value='' placeholder='#{l['to']}'></div>
	<div class='col' align='center'><button class='btn btn-sm btn-outline-danger' type='button' onclick="exUnit( '#{code}' )">#{l['exe']}</button></div>
	</div>

HTML

puts html
