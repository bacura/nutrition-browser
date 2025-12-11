#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 koyomi 0.2.8 (2025/09/17)


#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

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
	l['jp'] = {
		koyomi:      'こよみ:食事',
		sun:         '日',
		mon:         '月',
		tue:         '火',
		wed:         '水',
		thu:         '木',
		fri:         '金',
		sat:         '土',
		year:        '年',
		breakfast:   '朝食',
		lunch:       '昼食',
		dinner:      '夕食',
		supply:      '間食 / 補食',
		memo:        'メモ',
		foodrec:     '食事記録',
		exrec:       '拡張記録',
		calc:        '栄養計算',
		compo:       '食品構成',
		g100:        '100 g相当',
		food_n:      '食品名',
		food_g:      '食品群',
		weight:      '重量(g)',
		palette:     'パレット',
		snow:        '<img src=\'bootstrap-dist/icons/snow2.svg\' style=\'height:1.2em; width:1.2em;\'>',
		visionnerz:  '<img src=\'bootstrap-dist/icons/graph-up.svg\' style=\'height:2em; width:1.0em;\'>',
		chat_dots:   '<img src=\'bootstrap-dist/icons/chat-dots.svg\' style=\'height:2em; width:1.0em;\'>',
		return:      '<img src=\'bootstrap-dist/icons/geo.svg\' style=\'height:2em; width:2em;\'>'
	}

	return l[language]
end

####
def sub_menu( l )
	html = <<-"MENU"
<div class='container-fluid'>
	<span class='btn badge rounded-pill ppill' onclick="initKoyomi()">#{l[:foodrec]}</span>&nbsp;
	<span class='btn badge rounded-pill ppill' onclick="initKoyomiex()">#{l[:exrec]}</span>&nbsp;
	<span class='btn badge rounded-pill ppill' onclick="initKoyomiCalc()">#{l[:calc]}</span>&nbsp;
	<span class='btn badge rounded-pill ppill' onclick="initKoyomiCompo()">#{l[:compo]}</span>&nbsp;
</div>

MENU
	puts html
	exit()
end


####
def meals_html( solid, db )
	mb_html = '<ul>'
	solid.split( "\t" ).each do |e|
		code = e.split( '~' )[0]
		if /^\?/ =~ code
			tmp = "<li style='list-style-type: circle'>#{@something[code]}</li>"

		elsif /\-m\-/ =~ code
			puts 'menu' if @debug
			menu = Menu.new( db.user )
			tmp = menu.load_db( code, true ) ? "<li>#{menu.name}</li>" : "<li class='error'>Error: #{code}</li>"

		elsif /\-z\-/ =~ code
			puts 'fix' if @debug

			fix = FCT.new( db.user, @fct_item, @fct_name, @fct_unit, @fct_frct )
			tmp = fix.load_fcz( 'fix', code ) ? "<li style='list-style-type: circle'>#{fix.zname}</li>" : "<li class='error'>Error: #{code}</li>"
		elsif /\-/ =~ code
			puts 'recipe' if @debug
			recipe= Recipe.new( db.user )
			tmp = recipe.load_db( code, true ) ? "<li>#{recipe.name}</li>" : "<li class='error'>Error: #{code}</li>"
		
		else
			puts 'food' if @debug
			food = Food.new( db.user, code )
			tmp = food.load_tag ? "<li style='list-style-type: square'>#{food.name}</li>" : "<li class='error'>Error: #{code}</li>"

		end
		mb_html << tmp
	end
	mb_html << '</ul>'

	return mb_html
end


#def media_html( yyyy, mm, dd, tdiv, db )
#	html = ''
#	r = db.query( "SELECT code, zidx FROM #{$MYSQL_TB_MEDIA} WHERE user='#{db.user.name}' AND origin='#{yyyy}-#{mm}-#{dd}-#{tdiv}' AND type='jpg' ORDER BY zidx;", false )
#	r.each do |e|
#		html << "<img src='#{$PHOTO}/#{e['code']}-tns.jpg' class='photo_tns' onclick=\"modalPhoto( '#{e['code']}' )\">"
#	end

#	return html
#end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )

#### Guild member check
if user.status < 3
	puts "Guild member error."
#	exit
end


#### Getting POST
command = @cgi['command']
yyyy = @cgi['yyyy'].to_i
mm = @cgi['mm'].to_i
dd = @cgi['dd'].to_i
yyyy_mm = @cgi['yyyy_mm']
yyyy, mm = yyyy_mm.split( '-' ).map( &:to_i ) unless yyyy_mm == ''
dd = 1 if dd == 0
freeze_check = @cgi['freeze_check']
freeze_all_check = @cgi['freeze_all_check']

if @debug
	puts "command:#{command}<br>\n"
	puts "yyyy:#{yyyy}<br>\n"
	puts "mm:#{mm}<br>\n"
	puts "dd:#{dd}<br>\n"
	puts "freeze_check:#{freeze_check}<br>\n"
	puts "freeze_all_check:#{freeze_all_check}<br>\n"
	puts "<hr>\n"
end


#### Sub menu
sub_menu ( l ) if command == 'menu'


puts "Date & calendar config<br>" if @debug
calendar = Calendar.new( user, yyyy, mm, dd )
calendar_td = Calendar.new( user, 0, 0, 0 )
calendar.debug if @debug


puts "Koyomi config<br>" if @debug
koyomi = Koyomi.new( user )
koyomi.load_db( calendar.ymdf, calendar.ymdl )


puts "Freeze process<br>" if @debug
case command
when 'freeze'
	koyomi.freeze( calendar.ymd, 'all', freeze_check == 'true' )
when 'freeze_all'
	koyomi.freeze_all( calendar.ymd, freeze_all_check == 'true' )
end


puts "Palette setting<br>" if @debug
palette = Palette.new( user )
palette.set_bit( $PALETTE_DEFAULT_NAME[user.language][0] )

puts "html parts<br>" if @debug
fct_day_htmls = ['']

fct_day = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
fct_day.load_palette( palette.bit )

fct_tdiv = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
fct_tdiv.load_palette( palette.bit )

puts "koyomi matrix calc<br>" if @debug
1.upto( calendar.ddl ) do |day|
	 dds = day < 10 ? "0#{day}" : day.to_s
	 ymd = calendar.ym + '-' + dds
	if koyomi.solid[ymd]
		code_set, rate_set, unit_set = [], [], []
		fct_day.flash

		4.times do |tdiv|
			fct_tdiv.flash
			code_set, rate_set, unit_set = [], [], []

			if koyomi.fz_bit[ymd][tdiv] == 1

				puts "Freeze:#{koyomi.fz_code[ymd]}<br>" if @debug
				fct_day.into_solid( fct_tdiv.solid[0] ) if fct_tdiv.load_fcz( 'freeze', koyomi.fz_code[ymd][tdiv] )
			else
				puts 'Row<br>' if @debug
				if koyomi.solid[ymd][tdiv].to_s != ''
					koyomi.solid[ymd][tdiv].split( "\t" ).each do |e|
						code_, rate_, unit_ = e.split( '~' )
						code_set << code_
						rate_set << rate_
						unit_set << unit_
					end
				end
				code_set.each.with_index do |code, i|
					rate = food_weight_check( rate_set[i] ).last
					unit = unit_set[i]
					recipe_codes = []

					case code
					when /\?/
						fct_day.into_zero
					when /\-z\-/
						puts 'FIX<br>' if @debug
						fct_tdiv.load_fcz( 'fix', code )
					else
						puts 'Recipe<br>' if @debug
						recipe_codes = /\-m\-/.match?( code ) ? menu2rc( user, code ) : [code]

						food_nos, food_weights = [], []

						recipe_codes.each do |recipe_code|
							if /\-r\-/ =~ recipe_code || /\w+\-\h{4}\-\h{4}/ =~ recipe_code
								fns, fws = recipe2fns( user, recipe_code, rate, unit, 1 )[0..1]
								food_nos.concat( fns )
								food_weights.concat( fws )
							else
								food_nos << code
								food_weights << unit_weight( rate, unit, code )
							end
						end
						puts 'Foods<br>' if @debug
						fct_tdiv.set_food( food_nos, food_weights, false )
					end
				end

				puts 'Start calculation<br>' if @debug
				fct_tdiv.calc
				fct_tdiv.digit
				fct_day.into_solid( fct_tdiv.total )

				if fct_tdiv.foods.size > 0
					puts "freeze process<br>" if @debug
					koyomi.fz_code[ymd][tdiv] = fct_tdiv.save_fcz( nil, 'freeze', "#{ymd}-#{tdiv}" )
					koyomi.updates << ymd
				else
					fcz = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
					fcz.delete_fcz( 'freeze', nil, "#{ymd}-#{tdiv}" )
				end
			end
		end

		puts "Summary#{day} html<br>" if @debug
		fct_day.calc
		fct_day.digit
		pfc = fct_day.calc_pfc

		summary_html = fct_day.names.each_with_index.map do |name, i| "#{name}[#{fct_day.total[i]}]&nbsp;&nbsp;&nbsp;&nbsp;" end.join
		if pfc.size == 3
			summary_html << "&nbsp;&nbsp;<span style='color:crimson'>P</span>:<span style='color:green'>F</span>:<span style='color:blue'>C</span> (%) = "
			summary_html << "<span style='color:crimson'>#{pfc[0]}</span> : <span style='color:green'>#{pfc[1]}</span> : <span style='color:blue'>#{pfc[2]}</span>"
			summary_html << "&nbsp;&nbsp;<span onclick=\"initVisionnerz( '#{ymd}' )\">#{l[:visionnerz]}</span>" if user.status >= 5
			summary_html << "&nbsp;&nbsp;<span onclick=\"bridgeNote( '#{ymd}', '' )\">#{l[:chat_dots]}</span>" if user.status >= 5
		end
		fct_day_htmls << summary_html
	else
		fct_day_htmls << ''
	end
end
#@debug = true


puts "Day process<br>" if @debug
date_html = ''
week_count = calendar.wf
weeks = [l[:sun], l[:mon], l[:tue], l[:wed], l[:thu], l[:fri], l[:sat]]
photo = Media.new( user )
photo.base = 'koyomi'
1.upto( calendar.ddl ) do |day|
	puts "Day #{day}<br>" if @debug
	dds = day < 10 ? "0#{day}" : day.to_s
	ymd = calendar.ym + '-' + dds
	freeze_flag = false

	onclick = "onclick=\"initKoyomiEdit( '#{calendar.yyyy}', '#{calendar.mm}', '#{day}' )\""
	tmp_html = ''
	if koyomi.solid[ymd]
		5.times do |tdiv|
			tmp = "<div class='row' #{onclick}><div class='col'>-</div></div>"
			if koyomi.solid[ymd][tdiv].to_s != ''
				if tdiv < 4
					tmp = "<div class='row' #{onclick}><div class='col'>"
					tmp << meals_html( koyomi.solid[ymd][tdiv], db )
					tmp << '</div></div>'

					photo.origin = "#{ymd}-#{tdiv}"
					photo.get_series()
					photo.html_series_mini()
					tmp << photo.html_series_mini()
				else
					tmp = koyomi.solid[ymd][4]
				end

				freeze_flag = true if koyomi.fz_bit[ymd][tdiv] == 1
			end
			tmp_html << "<td>#{tmp}</td>"
		end
	else
		5.times do tmp_html << "<td #{onclick}>-</td>" end
	end

	style = ''
	style = 'color:red;' if week_count == 0
	date_html << "<tr id='day#{day}'>"
	date_html << "<td align='center' rowspan=2 style='#{style}'><span>#{day}</span> (#{weeks[week_count]})"
	date_html << "<br><br><input type='checkbox' id='freeze_check#{day}' onChange=\"freezeKoyomi( '#{day}' )\" #{$CHECK[freeze_flag]}>" if koyomi.solid[ymd]
	date_html << "</td>"
	date_html << tmp_html
	date_html << "</tr>"

	date_html << "<tr>"
	date_html << "<td colspan='5'>#{fct_day_htmls[day]}</td>" if fct_day_htmls[day] != nil
	date_html << "</tr>"

	week_count += 1
	week_count = 0 if week_count > 6
end


joystic_goto = calendar_td.dd - 1
joystic_goto = 1 if joystic_goto < 1


puts "HTML process<br>" if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-2'><h5>#{l[:koyomi]}</h5></div>
		<div class='col-2 form-inline'>
			<input type='month' class='form-control form-control-sm' id='yyyy_mm' min='#{calendar.yyyyf}-01' max='#{calendar.yyyy + 2}-01' value='#{calendar.yyyy}-#{calendar.mms}' onChange="changeKoyomi()">
		</div>
		<div align='center' class='col-8 joystic_koyomi' onclick="window.location.href='#day#{joystic_goto}';">#{l[:return]}</div>
	</div>
	<br>

	<table class="table table-sm">
	<thead class="table-light">
    	<tr>
     		<th align='center'>
     			<div class="form-check">
					<span onclick="freezeKoyomiAll()">#{l[:snow]}</span>
				</div>
     		</th>
     		<th align='center' width='15%'>#{l[:breakfast]}</th>
     		<th align='center' width='15%'>#{l[:lunch]}</th>
     		<th align='center' width='15%'>#{l[:dinner]}</th>
     		<th align='center' width='15%'>#{l[:supply]}</th>
     		<th align='center'>#{l[:memo]}</th>
    	</tr>
  	</thead>
	#{date_html}
	</table>
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================
koyomi.save_db unless command == 'init'
koyomi.delete_empty_db if command == 'init'

#==============================================================================
#FRONT SCRIPT
#==============================================================================
if command == 'init'
	js = <<~JS
<script type='text/javascript'>

var postReq = ( command, data, successCallback ) => {
	$.post( kp + '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
}

var changeKoyomi = () => {
	const yyyy_mm = $( '#yyyy_mm' ).val();
	postReq( 'change', { yyyy_mm }, data => {
		$( "#L1" ).html( data );
	});
}

var freezeKoyomi = ( dd ) => {
	const yyyy_mm = $( '#yyyy_mm' ).val();
	const freeze_check = $( `#freeze_check${dd}` ).is( ":checked" );
	postReq( 'freeze', { yyyy_mm, dd, freeze_check }, data => {
		$( "#L1" ).html( data );
	});
}

var freezeKoyomiAll = () => {
	let allChecked = true;
	for ( let day = 1; ; day++ ){
		const checkbox = document.getElementById( `freeze_check${day}` );
		if( !checkbox ) break; // チェックボックスが存在しない場合ループ終了
		if( !checkbox.checked ) allChecked = false;
	}
	const freeze_all_check = allChecked ? 'true' : 'false';

	const yyyy_mm = $( '#yyyy_mm' ).val();
	postReq( 'freeze_all', { yyyy_mm, freeze_all_check }, data => {
		$( "#L1" ).html( data );
	});
}

// Note book bridge
//var bridgeNote = ( code, origin ) => {
//	$.post( "note-bridge.cgi", { command:'text', base:'koyomi', origin:origin, code:code }, function( data ){ $( "#LF" ).html( data );});
//
//	displayVIDEO( 'Briged' );

//	flashBW();
//	dlf = true;
//	displayBW();
//};

JS

	puts js
end

#puts '<br>(^q^)' if @debug
