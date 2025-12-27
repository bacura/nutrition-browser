#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 koyomi adding panel 0.3.3 (2025/01/04)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
#script = File.basename( $0, '.cgi' )

#==============================================================================
# LIBRARY
#==============================================================================
require '../soul'
require '../brain'
require '../body'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		'koyomi' 	=> "こよみ:食事",\
		'sun' 		=> "日",\
		'mon' 		=> "月",\
		'tue' 		=> "火",\
		'wed' 		=> "水",\
		'thu' 		=> "木",\
		'fri' 		=> "金",\
		'sat' 		=> "土",\
		'year' 		=> "年",\
		'breakfast' => "朝食",\
		'lunch' 	=> "昼食",\
		'dinner' 	=> "夕食",\
		'supply'	=> "間食 / 補食",\
		'save' 		=> "登　録",\
		'volume' 	=> "量",\
		'time'		=> "分間",\
		'modify'	=> "変　更",\
		'copy' 		=> "複　製",\
		'inheritance'=> "時間継承",\
		'return' 	=> "<img src='bootstrap-dist/icons/signpost-r.svg' style='height:2em; width:2em;'>",\
		'joystick' 	=> "<img src='bootstrap-dist/icons/geo.svg' style='height:2em; width:2em;'>",\
		'clock'		=> "<img src='bootstrap-dist/icons/clock.svg' style='height:1.5em; width:1.5em;'>",\
		'calendar'	=> "<img src='bootstrap-dist/icons/calendar.svg' style='height:2em; width:2em;'>",\
		'return2'	=> "<img src='bootstrap-dist/icons/signpost.svg' style='height:2em; width:2em;'>"
	}

	return l[language]
end


#### unit select
def unit_select_html( code, selectu, db )
	# 単位の生成と選択
	unit_select_html = ''
	unit_set = []
	unit_select = []
	r = db.query( "SELECT unit FROM #{$TB_EXT} WHERE FN='#{code}';", false )
	if r.first
		unith = JSON.parse( r.first['unit'] )
		unith.each do |k, v|
			unless k == 'note'
				unit_set << k
				if k == selectu
					unit_select << 'SELECTED'
				else
					unit_select << ''
				end
			end
		end
	end

	unit_set.size.times do |c|
		unit_select_html << "<option value='#{unit_set[c]}' #{unit_select[c]}>#{unit_set[c]}</option>"
	end

	return unit_select_html
end


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )


#### Getting POST
command = @cgi['command']
yyyy = @cgi['yyyy'].to_i
mm = @cgi['mm'].to_i
dd = @cgi['dd'].to_i
yyyy_mm_dd = @cgi['yyyy_mm_dd']
unless yyyy_mm_dd == ''
	a = yyyy_mm_dd.split( '-' )
	yyyy = a[0].to_i
	mm = a[1].to_i
	dd = a[2].to_i
end
code = @cgi['code']
ev = @cgi['ev']
eu = @cgi['eu']
tdiv = @cgi['tdiv'].to_i
hh_mm = @cgi['hh_mm']
meal_time = @cgi['meal_time'].to_i
order = @cgi['order'].to_i
copy = @cgi['copy'].to_i
carry_on = @cgi['carry_on']
carry_on = 1 if @cgi['carry_on'] == ''
carry_on = carry_on.to_i
origin = @cgi['origin']
dd = 1 if dd == 0
ev = 100 if ev == 0 || ev == '' || ev == nil
origin_date = origin.split( ':' )
origin = "#{yyyy}:#{mm}:#{dd}:#{tdiv}:#{order}" if ( command == 'modify' || command == 'fzcopy' ) && origin == ''

if @debug
	puts "command:#{command}<br>\n"
	puts "code:#{code}<br>\n"
	puts "yyyy_mm_dd:#{yyyy_mm_dd}<br>\n"
	puts "hh_mm:#{hh_mm}<br>\n"
	puts "meal_time:#{meal_time}<br>\n"
	puts "tdiv:#{tdiv}<br>\n"
	puts "ev:#{ev}<br>\n"
	puts "eu:#{eu}<br>\n"
	puts "order:#{order}<br>\n"
	puts "copy:#{copy}<br>\n"
	puts "carry_on:#{carry_on}<br>\n"
	puts "origin:#{origin}<br>\n"
	puts "<hr>\n"
end


puts 'SET date & calendar config<br>' if @debug
calendar = Calendar.new( user, yyyy, mm, dd )
calendar.debug if @debug
sql_ymd = "#{calendar.yyyy}-#{calendar.mm}-#{calendar.dd}"
sql_ym = "#{calendar.yyyy}-#{calendar.mm}"
org_ymd = "#{calendar.yyyy}:#{calendar.mm}:#{calendar.dd}"


puts 'SET koyomi start year<br>' if @debug
r = db.query( "SELECT koyomi FROM #{$TB_CFG} WHERE user='#{user.name}';", false )
if r.first
	if r.first['koyomi'] != nil && r.first['koyomi'] != ''
		koyomi_cfg = JSON.parse( r.first['koyomi'] )
		start_yesr = koyomi_cfg['start'].to_i
		p koyomi_cfg if @debug
	end
end


puts 'SET standard meal start & time<br>' if @debug
start_time_set = []
meal_tiems_set = []
r = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user='#{user.name}';", false )
if r.first
	if r.first['bio'] != nil && r.first['bio'] != ''
		bio = JSON.parse( r.first['bio'] )
		start_times_set = [bio['bst'], bio['lst'], bio['dst']]
		meal_tiems_set = [bio['bti'].to_i, bio['lti'].to_i, bio['dti'].to_i]

		hh_mm = start_times_set[tdiv] if hh_mm == '' || hh_mm == nil
		meal_time = meal_tiems_set[tdiv] if meal_time == 0
	end
end
hh_mm = '00:00' if hh_mm == nil || hh_mm == ''
meal_time = 20 if meal_time == nil || meal_time == '' || meal_time == 0


new_solid = ''
#Removing pre-koyomi
if ( command == 'move' && copy != 1 ) || ( command == 'fixcopy' && copy != 1 )
	puts 'Move food (deleting origin )<br>' if @debug
	a = origin.split( ':' )
	r = db.query( "SELECT * FROM #{$TB_KOYOMI} WHERE user='#{user.name}' AND date='#{a[0]}-#{a[1]}-#{a[2]}' AND tdiv='#{a[3]}';", false )
	if r.first['koyomi']
		t = r.first['koyomi']
		aa = t.split( "\t" )
		0.upto( aa.size - 1 ) do |c|
			new_solid << "#{aa[c]}\t" unless c == a[4].to_i
		end
		new_solid.chop! unless new_solid == ''
	end
	db.query( "UPDATE #{$TB_KOYOMI} SET koyomi='#{new_solid}' WHERE user='#{user.name}' AND date='#{a[0]}-#{a[1]}-#{a[2]}' AND tdiv='#{a[3]}';", true )
end

#Saving post-koyomi
if command == 'save' || command == 'move' || command == 'fixcopy' || command == 'fzcopy'

	if command == 'fixcopy' && copy == 1
		puts 'Duplicate fix<br>' if @debug
		db.query( "CREATE TEMPORARY TABLE tt AS SELECT * FROM #{$TB_FCZ} WHERE code='#{code}';", true )
		new_fix_code = generate_code( user.name, 'z' )
		db.query( "UPDATE tt SET code='#{new_fix_code}' WHERE code='#{code}';", true )
		db.query( "INSERT INTO #{$TB_FCZ} SELECT * FROM tt WHERE code='#{new_fix_code}';", true )
		code = new_fix_code
	end

	puts 'Save food<br>' if @debug
	r = db.query( "SELECT * FROM #{$TB_KOYOMI} WHERE user='#{user.name}' AND date='#{sql_ymd}' AND tdiv='#{tdiv}';", false )
	if r.first
		koyomi = r.first['koyomi']
		delimiter = ''
		if koyomi != ''
			delimiter = "\t"
			if carry_on == 1
				a = koyomi.split( delimiter )
				aa = a.last.split( '~' )
				hh_mm = aa[3]
				meal_time = aa[4]
			end
		end
		koyomi << "#{delimiter}#{code}~#{ev}~#{eu}~#{hh_mm}~#{meal_time}"

		db.query( "UPDATE #{$TB_KOYOMI} SET koyomi='#{koyomi}' WHERE user='#{user.name}' AND date='#{sql_ymd}' AND tdiv='#{tdiv}';", true )
		origin = "#{org_ymd}:#{tdiv}:#{koyomi.split( "\t" ).size - 1}" if command == 'move' || command == 'fixcopy'
	else
		koyomi = "#{code}~#{ev}~#{eu}~#{hh_mm}~#{meal_time}"
		db.query( "INSERT INTO #{$TB_KOYOMI} SET user='#{user.name}', fzcode='', freeze='0', koyomi='#{koyomi}', date='#{sql_ymd}', tdiv='#{tdiv}';", true )
		origin = "#{org_ymd}:#{tdiv}:0" if command == 'move' || command == 'fixcopy'
	end
end

copy_html = ''
save_button = "<button class='btn btn-sm btn-info' type='button' onclick=\"saveKoyomiAdd( 'save', '#{code}', '#{origin}' )\">#{l['save']}</button>"
####
if command == 'modify' || command == 'move' || command == 'fix_direct' || command == 'fixcopy'
	copy_html << "<div class='form-group form-check'>"
    copy_html << "<input type='checkbox' class='form-check-input' id='copy' #{$CHECK[copy]}>"
    copy_html << "<label class='form-check-label'>#{l['copy']}</label>"
	copy_html << "</div>"

	save_button = "<button class='btn btn-sm btn-info' type='button' onclick=\"saveKoyomiAdd( 'move', '#{code}', '#{origin}' )\">#{l['modify']}</button>"
elsif command == 'fzc_mode' || command == 'fzcopy'
	copy_html << "<div class='form-group form-check'>"
    copy_html << "<input type='checkbox' class='form-check-input' id='copy' CHECKED DISABLED>"
    copy_html << "<label class='form-check-label'>#{l['copy']}</label>"
	copy_html << "</div>"
	save_button = ""
end


####
food_name = code
if /\-m\-/ =~ code
	r = db.query( "SELECT name FROM #{$TB_MENU} WHERE code='#{code}' and user='#{user.name}';", false )
	food_name = r.first['name']
elsif /\-z\-/ =~ code
	r = db.query( "SELECT name FROM #{$TB_FCZ} WHERE code='#{code}' and user='#{user.name}';", false )
	food_name = r.first['name']
elsif /\-/ =~ code
	r = db.query( "SELECT name FROM #{$TB_RECIPE} WHERE code='#{code}' and user='#{user.name}';", false )
	food_name = r.first['name']
else
	q = "SELECT name FROM #{$TB_TAG} WHERE FN='#{code}';"
	q = "SELECT name FROM #{$TB_TAG} WHERE FN='#{code}' AND user='#{user.name}';" if /^U\d{5}/ =~ code
	r = db.query( q, false )
	food_name = r.first['name']
end


puts "koyomi matrix<br>" if @debug
koyomi_mx = []
kfreeze_flags = []
31.times do |i| koyomi_mx[i + 1] = Array.new end
r = db.query( "SELECT * FROM #{$TB_KOYOMI} WHERE user='#{user.name}' AND koyomi!='' AND koyomi IS NOT NULL AND date BETWEEN '#{sql_ym}-1' AND '#{sql_ym}-31';", false )
r.each do |e|
	koyomi_mx[e['date'].day][e['tdiv']] = e
	kfreeze_flags[e['date'].day] = true if e['freeze'] == 1
end


#### Date HTML
date_html = ''
week_count = calendar.wf
weeks = [l['sun'], l['mon'], l['tue'], l['wed'], l['thu'], l['fri'], l['sat']]
1.upto( calendar.ddl ) do |day_|
	kmrd = koyomi_mx[day_]
	date_html << "<tr id='day#{day_}'>"
	style = ''
	style = 'color:red;' if week_count == 0
	onclick = "onclick=\"editKoyomi( '#{calendar.yyyy}-#{calendar.mm}-#{day_}' )\""
	date_html << "<td style='#{style}' #{onclick}>#{day_} (#{weeks[week_count]})</td>"

	unless kfreeze_flags[day_]
		4.times do |tdiv_|
			koyomi_c = '-'
			kmre = koyomi_mx[day_][tdiv_]

			onclick = ''
			case command
			when 'modify', 'move'
				onclick = "onclick=\"k2Koyomi_direct( 'move', '#{code}','#{calendar.yyyy}','#{calendar.mm}', '#{day_}', '#{tdiv_}', '#{origin}' )\""
			when 'fix_direct', 'fixcopy'
				onclick = "onclick=\"k2Koyomi_direct( 'fixcopy', '#{code}','#{calendar.yyyy}','#{calendar.mm}', '#{day_}', '#{tdiv_}', '#{origin}' )\""
			when 'fzc_mode', 'fzcopy'
				onclick = "onclick=\"k2Koyomi_direct( 'fzcopy', '#{code}','#{calendar.yyyy}','#{calendar.mm}', '#{day_}', '#{tdiv_}', '#{origin}' )\""
			else
				onclick = "onclick=\"saveKoyomiAdd_direct( '#{code}','#{calendar.yyyy}','#{calendar.mm}', '#{day_}', '#{tdiv_}', '#{origin}' )\""
			end

			bs_class = 'table-light'
			if kmre
				if kmre['koyomi'] != ''
					koyomi_c = kmre['koyomi'].split( "\t" ).size
					if dd == day_ and tdiv == tdiv_
						bs_class = 'table-warning'
					else
						bs_class = 'table-info'
					end
				end
			end
			date_html << "<td class='#{bs_class}' align='center' #{onclick}>#{koyomi_c}</td>"
		end
	else
		4.times do date_html << "<td class='table-secondary'></td>" end
	end

	date_html << "</tr>"
	week_count += 1
	week_count = 0 if week_count > 6
end


#### Select HTML
tdiv_set = [ l['breakfast'], l['lunch'], l['dinner'], l['supply'] ]
tdiv_html = ''
tdiv_html << "<select id='tdiv' class='form-select form-select-sm'>"
0.upto( 3 ) do |c| tdiv_html << "<option value='#{c}' #{$SELECT[c == tdiv]}>#{tdiv_set[c]}</option>" end
tdiv_html << "</select>"


puts 'SELECT HH block<br>' if @debug
meal_time_set = [5, 10, 15, 20, 30, 45, 60, 90, 120 ]
eat_time_html = "<div class='input-group input-group-sm'>"
eat_time_html << "<label class='input-group-text btn-info' onclick=\"nowKoyomi( 'hh_mm' )\">#{l['clock']}</label>"
eat_time_html << "<input type='time' step='60' id='hh_mm' value='#{hh_mm}' class='form-control' style='min-width:100px;'>"
eat_time_html << "<select id='meal_time' class='form-select form-select-sm'>"
meal_time_set.each do |e|
	if meal_time == e
		eat_time_html << "	<option value='#{e}' SELECTED>#{e}</option>"
	else
		eat_time_html << "	<option value='#{e}'>#{e}</option>"
	end
end
eat_time_html << "</select>"
eat_time_html << "<label class='input-group-text'>#{l['time']}</label>"
eat_time_html << "</div>"


#### Rate HTML
rate_selected = ''
rate_html = ''
if command == 'fix_direct' || command == 'fix_copy' || /\-f\-/ =~ code
	rate_html << "	<input type='hidden' id='ev' value='#{ev}'>"
	rate_html << "	<input type='hidden' id='eu' value='#{eu}'>"
else
	rate_selected = 'SELECTED' if /^[UP]?\d{5}/ =~ code
	rate_html << "<div class='input-group input-group-sm'>"
	rate_html << "	<label class='input-group-text'>#{l['volume']}</label>"
	rate_html << "	<input type='text' id='ev' value='#{ev}' class='form-control'>"
	rate_html << "	<select id='eu' class='form-select form-select-sm'>"
	if /^[UP]?\d{5}/ =~ code
		rate_html << unit_select_html( code, eu, db )
	else
		rate_html << "		<option value='%'>%</option>"
		rate_html << "		<option value='g' #{rate_selected}>g</option>"
		rate_html << "		<option value='kcal'>kcal</option>"
	end
	rate_html << "	</select>"
	rate_html << "</div>"
end


#### Return button
return_joystic = ''
if command == 'modify' || command == 'move' || command == 'fix_direct' || command == 'fzc_mode' || command == 'fzcopy'
	return_joystic = "<div align='center' class='col-4 joystic_koyomi' onclick=\"koyomiReturn()\">#{l['return']}</div>"
else
	return_joystic = "<div align='center' class='col-2 joystic_koyomi' onclick=\"koyomiReturn2KE( '#{origin_date[0]}', '#{origin_date[1]}', '#{origin_date[2]}' )\">#{l['return']}</div>"
	return_joystic << "<div align='center' class='col-2 joystic_koyomi' onclick=\"koyomiReturn2KE( '#{calendar.yyyy}', '#{calendar.mm}', '#{calendar.dd}' )\">#{l['return2']}</div>"
end


#### carry_on_check
carry_on_html = "<input class='form-check-input' type='checkbox' id='carry_on' #{$CHECK[carry_on]}>"
carry_on_html << "<label class='form-check-label'>#{l['inheritance']}</label>"


onchange = "onChange=\"changeKoyomiAdd( 'init', '#{code}', '#{origin}' )\""
onchange = "onChange=\"changeKoyomiAdd( 'modify', '#{code}', '#{origin}' )\"" if command == 'modify'


html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-3'><h5>#{food_name}</h5></div>
		<div align='center' class='col-2 joystic_koyomi' onclick="window.location.href='#day#{calendar.dd}';">#{l['joystick']}</div>
		<div align='center' class='col-3 joystic_koyomi' onclick="initKoyomi()">#{l['calendar']}</div>
		#{return_joystic}
	</div>
	<br>
	<div class='row'>
		<div class='col-2 form-inline'>
			<input type='date' class='form-control form-control-sm' id='yyyy_mm_dd' min='#{calendar.yyyyf}-01-01' max='#{calendar.yyyy + 2}-12-31' value='#{calendar.yyyy}-#{calendar.mms}-#{calendar.dds}' #{onchange}>
		</div>
		<div class='col-2 form-inline'>#{tdiv_html}</div>
		<div class='col-4 form-inline'>#{eat_time_html}</div>
		<div class='col-2 form-check'>#{carry_on_html}</div>
		<div class='col-2 form-check'>#{copy_html}</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-4 form-inline'>#{rate_html}</div>
	</div>
	<br>

	<div class='row'>#{save_button}</div>
	<br>

	<table class="table table-sm table-hover">
	<thead>
    	<tr>
     		<th align='center'></th>
     		<th align='center'>#{l['breakfast']}</th>
     		<th align='center'>#{l['lunch']}</th>
     		<th align='center'>#{l['dinner']}</th>
     		<th align='center'>#{l['supply']}</th>
    	</tr>
  	</thead>
	#{date_html}
	</table>
HTML
puts html

#==============================================================================
# POST PROCESS
#==============================================================================

#### Adding history
add_his( user, code ) if /\d{5}/ =~ code || /\-r\-/ =~ code
