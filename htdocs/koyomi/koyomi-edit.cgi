#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 koyomi editor 0.2.8 (2025/02/25)

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
		breakfast: "朝食", \
		lunch:     "昼食", \
		dinner:    "夕食", \
		supply:    "間食 / 補食", \
		control:   "操作", \
		meal:      "食事内容", \
		volume:    "摂取量", \
		start:     "開始時刻", \
		period:    "食事時間", \
		some:      "何か食べた", \
		plus:      "＋", \
		copy:      "複製", \
		move:      "移動", \
		fixcpmv:   "固有編集", \
		memo:      "メモ", \
		clear:     "お片付け", \
		alt:       "キャプション", \
		return:    "<img src='bootstrap-dist/icons/signpost-r.svg' style='height:2em; width:2em;'>", \
		visionnerz:"<img src='bootstrap-dist/icons/graph-up.svg' style='height:2em; width:2em;'>", \
		write:     "<img src='bootstrap-dist/icons/pencil-square.svg' style='height:3em; width:3em;'>", \
		recipe:    "<img src='bootstrap-dist/icons/card-text.svg' style='height:1.2em; width:1.2em;'>", \
		camera:    "<img src='bootstrap-dist/icons/camera.svg' style='height:1.2em; width:1.2em;'>", \
		trashf:    "<img src='bootstrap-dist/icons/trash-fill.svg' style='height:1.2em; width:1.2em;'>", \
		trash:     "<img src='bootstrap-dist/icons/trash.svg' style='height:1.2em; width:1.2em;'>"
	}

	return l[language]
end

def meal_html(  db, l, calendar, solid, tdiv, freeze_flag  )
	return '' if solid.to_s.empty?

	mb_html = <<~HTML
	<table class='table table-sm table-hover'>
	<thead class="table-light">
	  <tr>
	    <td>#{l[:meal]}</td>
	    <td>#{l[:volume]}</td>
	    <td>#{l[:start]}</td>
	    <td>#{l[:period]}</td>
	    <td>#{l[:control]}</td>
	  </tr>
	</thead>
	HTML

	solid.split( "\t" ).each.with_index do |item, order| # ee
		code, wt, unit, hh_mm, meal_time = item.split( '~' )
		item_name = ''
		onclick = ''
		fix_copy_button = ''
		recipe_button = ''

		if /^\?/ =~ code
			item_name = @something[code]
		elsif /\-m\-/ =~ code
			menu = Menu.new( db.user )
			if menu.load_db( code, true )
				item_name = menu.name
				onclick = ""
			else
				item_name = "<span class='error'>ERROR: #{code}</span>"
			end
		elsif /\-z\-/ =~ code
			fix = FCT.new( db.user, @fct_item, @fct_name, @fct_unit, @fct_frct )

			if fix.load_fcz( 'fix', code )
				item_name = fix.zname
				origin = "#{calendar.yyyy}:#{calendar.mm}:#{calendar.dd}:#{tdiv}:#{order}"
				onclick = " onclick=\"modifychangeKoyomiFC( '#{code}', '#{origin}' )\"" unless freeze_flag
				fix_copy_button = "<span class='badge bg-primary' onclick=\"modifyKoyomiFix( '#{code}', '#{calendar.yyyy}', '#{calendar.mm}', '#{calendar.dd}', '#{tdiv}', '#{hh_mm}', '#{meal_time}', '#{order}' )\">#{l[:fixcpmv]}</span>"
			else
				item_name = "<span class='error'>ERROR: #{code}</span>"
			end
		elsif /\-/ =~ code
			recipe= Recipe.new( db.user )
			if recipe.load_db( code, true )
				item_name = recipe.name
				onclick = " onclick=\"modifyKoyomi( 'modify', '#{code}', '#{calendar.yyyy}', '#{calendar.mm}', '#{calendar.dd}', '#{tdiv}', '#{hh_mm}', '#{meal_time}', '#{wt}', '#{unit}', '#{order}' )\"" unless freeze_flag
				recipe_button = "<span onclick=\"initCB( 'load', '#{code}' )\">#{l[:recipe]}</span>"
			else
				item_name = "<span class='error'>ERROR: #{code}</span>"
			end
		elsif code.to_s != ''
			food = Food.new( db.user, code )
			if food.load_tag
				item_name = food.name
				mode = freeze_flag ? 'fzc_mode' : 'modify'
 				onclick = " onclick=\"modifyKoyomi( '#{mode}', '#{code}', '#{calendar.yyyy}', '#{calendar.mm}', '#{calendar.dd}', '#{tdiv}', '#{hh_mm}', '#{meal_time}', '#{wt}', '#{unit}', '#{order}' )\""
			else
				item_name = "<span class='error'>ERROR: #{code}</span>"
			end
		else
			item_name = "<span class='error'>ERROR: #{code}</span>"
		end


		mb_html << "<tr>"
		mb_html << "<td#{onclick}>#{item_name}</td>"

		case code
		when /\-z\-/, /^\?/
		  mb_html << "<td#{onclick}>-</td>"
		when /\-m\-/, /\-/
		  mb_html << "<td#{onclick}>#{wt}&nbsp;#{unit}</td>"
		else
		  rate = food_weight_check( wt ).last
		  uw = unit != 'g' ? "&nbsp;(#{unit_weight(rate, unit, code).to_f} g)" : ''
		  mb_html << "<td#{onclick}>#{wt}&nbsp;#{unit}#{uw}</td>"
		end

		mb_html << "<td#{onclick}>#{hh_mm}</td>"
		mb_html << "<td#{onclick}>#{meal_time}</td>"

		unless freeze_flag
			mb_html << "<td>"
			mb_html << "<div class='row'>"

			mb_html << "	<div class='col-6'>"
			mb_html << fix_copy_button unless fix_copy_button == ''
			mb_html << recipe_button unless recipe_button == ''
			mb_html << "	</div>"

			mb_html << "<div class='col-6'>"
			mb_html << "	<span onclick=\"deleteKoyomi( '#{calendar.yyyy}', '#{calendar.mm}', '#{calendar.dd}', '#{tdiv}', '#{code}', '#{order}' )\">#{l[:trash]}</span>" if /^\?P/ !~ code
			mb_html << "</div>"

			mb_html << "</div>"
			mb_html << "</td>"
		else
			mb_html << "<td></td>"
		end

		mb_html << '</tr>'
	end
	mb_html << '</table>'

	return mb_html
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )

puts 'Getting POST<br>' if @debug
command = @cgi['command']

yyyy = @cgi['yyyy'].to_i
mm = @cgi['mm'].to_i
dd = @cgi['dd'].to_i
tdiv = @cgi['tdiv'].to_i

code = @cgi['code']
memo = @cgi['memo']
some = @cgi['some']
origin = @cgi['origin']
zidx = @cgi['zidx']

if @debug
	puts "command:#{command}<br>\n"
	puts "yyyy:#{yyyy}<br>\n"
	puts "mm:#{mm}<br>\n"
	puts "dd:#{dd}<br>\n"
	puts "tdiv:#{tdiv}<br>\n"
	puts "code:#{code}<br>\n"
	puts "memo:#{memo}<br>\n"
	puts "some: #{some}<br>\n"
	puts "origin: #{origin}<br>\n"
	puts "<hr>\n"
end


puts "Koyomi config<br>" if @debug
calendar = Calendar.new( user, yyyy, mm, dd )
ymd = calendar.ymd
koyomi = Koyomi.new( user )
koyomi.load_db( ymd )
freeze_flag = koyomi.freeze_flag( ymd )


case command
when 'delete'
	puts 'Deleting food<br>' if @debug
	order = @cgi['order'].to_i

	meals = koyomi.solid[ymd][tdiv].split( "\t" )
	meals.slice!( order )
	koyomi.modify( ymd, tdiv , meals.join( "\t" ))
	koyomi.updates << ymd

	if /\-z\-/ =~ code
		fcz = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct )
		fcz.delete_fcz( 'freeze', code )
	end

when 'memo'
	puts 'Updating memo<br>' if @debug
	koyomi.add( ymd, 4, memo )
	koyomi.updates << ymd

when 'some'
	puts 'Saving Something<br>' if @debug
	koyomi.add( ymd, tdiv, "#{some}~0~0~0~0" )
	koyomi.updates << ymd

when 'clear'
	puts 'Clear koyomi<br>' if @debug
	koyomi.clear( ymd, 'all' )
	fcz = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct )
	4.times do |tdiv| fcz.delete_fcz( 'freeze', "#{ymd}-#{tdiv}" ) end
	koyomi.updates << ymd

	photo = Media.new( user, 'koyomi' )
	0.upto( 3 ) do |tdiv|
		photo.origin = "#{ymd}-#{tdiv}"
		photo.delete_series( true )
	end

when 'photo_upload'
	new_photo = Media.new( user )
	new_photo.load_cgi( @cgi )
	new_photo.save_photo( @cgi )
    new_photo.get_series()
    new_photo.save_db()

when 'photo_mv'
	target_photo = Media.new( user )
	target_photo.load_cgi( @cgi )
    target_photo.get_series()
    target_photo.move_series()

when 'photo_del'
	target_photo = Media.new( user )
	target_photo.load_cgi( @cgi )
	target_photo.delete_photo( true )
	target_photo.delete_db( true )
end


puts 'Setting palette & FCT<br>' if @debug
palette = Palette.new( user )
palette.set_bit( $PALETTE_DEFAULT_NAME[user.language][0] )
fct = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
fct.load_palette( palette.bit )


puts 'Updaing media<br>' if @debug
target_photo = Media.new( user, 'koyomi' )
4.times do |tdiv|
	target_photo.origin = "#{ymd}-#{tdiv}"
	target_photo.get_series()
	if target_photo.series.size > 0
		koyomi.solid[ymd] = [] if koyomi.solid[ymd].nil?
		koyomi.add( ymd, tdiv, '?P' ) if koyomi.solid[ymd][tdiv].to_s == ''
	else
		next if koyomi.solid[ymd].nil?
		koyomi.clear( ymd, tdiv ) if koyomi.solid[ymd][tdiv] == '?P'
	end
end


puts 'Updaing freeze<br>' if @debug
koyomi_html = []
if koyomi.solid[ymd]
	koyomi.solid[ymd].each.with_index do |e, tdiv|
		if tdiv == 4
			koyomi_html[tdiv] = e
		else
			koyomi_html[tdiv] = meal_html( db, l, calendar, e, tdiv, freeze_flag )

			fct.flash
			code_set, rate_set, unit_set = [], [], []

			if koyomi.fz_bit[ymd][tdiv] == 1
				puts "Freeze:#{koyomi.fz_code[ymd]}<br>" if @debug
				fct.load_fcz( 'freeze', koyomi.fz_code[ymd][tdiv] )
				fct.calc
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
					when /\-z\-/
						puts 'FIX<br>' if @debug
						fct.load_fcz( 'fix', code )
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
						fct.set_food( food_nos, food_weights, false )
					end
				end

				puts 'Start calculation<br>' if @debug
				fct.calc
				fct.digit

				if fct.foods.size > 0
					puts "freeze process<br>" if @debug
					koyomi.fz_code[ymd][tdiv] = fct.save_fcz( nil, 'freeze', "#{ymd}-#{tdiv}" )
					koyomi.updates << ymd
				else
					fcz = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct )
					fcz.delete_fcz( 'freeze', "#{ymd}-#{tdiv}" )
				end
			end

			total_html = ''
			fct.total.size.times do |i| total_html << "#{fct.names[i]}[#{fct.total[i].to_f}]&nbsp;&nbsp;&nbsp;&nbsp;" end
			koyomi_html[tdiv] << total_html
		end
	end
end

####
cmm_html = [ '', '', '', '' ]
4.times do |tdiv|
	if freeze_flag
		cmm_html[tdiv]	<< "<button class='btn btn-sm btn-secondary'>#{l[:plus]}</button>&nbsp;"
	else
		cmm_html[tdiv]	<< "<button class='btn btn-sm btn-dark' onclick=\"initKoyomiFix( '#{yyyy}', '#{mm}', '#{dd}', '#{tdiv}' )\">#{l[:plus]}</button>&nbsp;"
	end
	if koyomi_html[tdiv] == nil
		cmm_html[tdiv] << "<button class='btn btn-sm btn-secondary'>#{l[:copy]}</button>&nbsp;"
		cmm_html[tdiv] << "<button class='btn btn-sm btn-secondary'>#{l[:move]}</button>&nbsp;"
	else
		cmm_html[tdiv] << "<button class='btn btn-sm btn-primary' onclick=\"cmmKoyomi( 'copy', '#{yyyy}', '#{mm}', '#{dd}', #{tdiv} )\">#{l[:copy]}</button>&nbsp;"
		cmm_html[tdiv] << "<button class='btn btn-sm btn-primary' onclick=\"cmmKoyomi( 'move', '#{yyyy}', '#{mm}', '#{dd}', #{tdiv} )\">#{l[:move]}</button>&nbsp;" unless freeze_flag == 1
	end
end


puts 'Setting something<br>' if @debug
some_html = [ '', '', '' ]
unless freeze_flag
	4.times do |tdiv|
		some_html[tdiv] = <<~SOME
		<select class='form-select form-select-sm' id='some#{tdiv}' onchange="koyomiSaveSome( '#{yyyy}', '#{mm}', '#{dd}', #{tdiv}, 'some#{tdiv}' )">
			<option value='' selected>#{l[:some]}</option>
			<option value='?--'>#{@something['?--']}</option>
			<option value='?-'>#{@something['?-']}</option>
			<option value='?='>#{@something['?=']}</option>
			<option value='?+'>#{@something['?+']}</option>
			<option value='?++'>#{@something['?++']}</option>
			<option value='?0'>#{@something['?0']}</option>
		</select>
SOME
	end
end


puts 'photo upload form<br>' if @debug
disabled = freeze_flag ? 'DISABLED' : ''

puts 'photo frame<br>' if @debug
photo_frame = []
4.times do |tdiv|
	photo = Media.new( user, 'koyomi' )
	photo.origin = "#{ymd}-#{tdiv}"
	photo.get_series()
	photo_frame[tdiv] = photo.html_series( '-tn', 100, freeze_flag )
end


####
memo_html = ''
unless freeze_flag
	memo_html = <<~MEMO1
	<div class='col-10'>
		<textarea class='form-control' id='memo' rows='2'>#{koyomi_html[4]}</textarea>
	</div>
	<div class='col-1'><br>
		<span onclick="memoKoyomi( '#{yyyy}', '#{mm}', '#{dd}' )">#{l[:write]}</span>
	</div>
MEMO1
else
	memo_html = <<~MEMO2
	<div class='col-10'>
		#{koyomi_html[4]}
	</div>
MEMO2
end


html = <<~HTML
<div class='container-fluid'>
	<div class='row'>
		<div class='col-2'><h5>#{yyyy} / #{mm} / #{dd}</h5></div>
		<div align='center' class='col-8 joystic_koyomi' onclick="reKoyomi( '#{yyyy}', '#{mm}' )">#{l[:return]}</div>
		<div align='center' class='col-2'>
			<input type='checkbox' id='check_kc' #{disabled}>&nbsp;
			<span class='badge rounded-pill npill' onclick="clearKoyomi( '#{yyyy}', '#{mm}', '#{dd}' )">#{l[:clear]}</span>
		</div>

	</div>
	<br>

	<div class='row'>
		<h6>#{l[:breakfast]}</h6>
		<div class='col-4'>
			<div class="input-group">
				#{cmm_html[0]}
				#{some_html[0]}
			</div>
		</div>
		<div class='col-3'></div>
		<div class='col-5'>#{}</div>
	</div>
	<div class='row'>
		<div class='col-7'>#{koyomi_html[0]}</div>
		<div class='col-5'>#{photo_frame[0]}</div>
	</div>
	<hr>

	<div class='row'>
		<h6>#{l[:lunch]}</h6>
		<div class='col-4'>
			<div class="input-group">
				#{cmm_html[1]}
				#{some_html[1]}
			</div>
		</div>
		<div class='col-3'></div>
		<div class='col-5'>#{}</div>
	</div>
	<div class='row'>
		<div class='col-7'>#{koyomi_html[1]}</div>
		<div class='col-5'>#{photo_frame[1]}</div>
	</div>
	<hr>

	<div class='row'>
		<h6>#{l[:dinner]}</h6>
		<div class='col-4'>
			<div class="input-group">
				#{cmm_html[2]}
				#{some_html[2]}
			</div>
		</div>
		<div class='col-3'></div>
		<div class='col-5'>#{}</div>
	</div>
	<div class='row'>
		<div class='col-7'>#{koyomi_html[2]}</div>
		<div class='col-5'>#{photo_frame[2]}</div>
	</div>
	<hr>

	<div class='row'>
		<h6>#{l[:supply]}</h6>
		<div class='col-4'>
			<div class="input-group">
				#{cmm_html[3]}
				#{some_html[3]}
			</div>
		</div>
		<div class='col-3'></div>
		<div class='col-5'>#{}</div>
	</div>
	<div class='row'>
		<div class='col-7'>#{koyomi_html[3]}</div>
		<div class='col-5'>#{photo_frame[3]}</div>
	</div>
	<br><br>

	<div class='row'>
		<div class='col-1'><h5>#{l[:memo]}</h5></div>
		#{memo_html}
	</div>
	<br>

	<div class='row'>
		<form method='post' enctype='multipart/form-data' id='koyomi_puf'>
		<div class="input-group input-group-sm">
			<div class='col-2'>
				<div class="input-group input-group-sm">
					<label class='input-group-text'>#{l[:camera]}</label>
					<select class='form-select form-select-sm' id='photo_tdiv' #{disabled}>
						<option value='0'>#{l[:breakfast]}</option>
						<option value='1'>#{l[:lunch]}</option>
						<option value='2'>#{l[:dinner]}</option>
						<option value='3'>#{l[:supply]}</option>
					</select>
				</div>
			</div>
			<div class='col-6'>
				<div class="input-group input-group-sm">
					<label class='input-group-text' for="alt">#{l[:alt]}</label>
					<input type='text' maxlength='120' id='alt' class='form-control form-control-sm' #{disabled}>
				</div>
			</div>
			<div class='col-4'>
				<input type='file' class='form-control form-control-sm' name='photo' onchange="PhotoUpload( '#{ymd}' )" #{disabled}>
			</div>
		</div>
		</form>
	</div>
</div>

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
	js = <<-"JS"
<script type='text/javascript'>

var base = 'koyomi';
var layer = '#L2';

var postReq_ke = ( command, data, successCallback ) => {
	$.post( kp + '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
}

// Koyomi delete
var deleteKoyomi = ( yyyy, mm, dd, tdiv, code, order ) => {
	postReq_ke( 'delete', { yyyy, mm, dd, tdiv, code, order }, data => {
		$( layer ).html( data );
	});
}

// Koyomi memo
var memoKoyomi = (yyyy, mm, dd) => {
	const memo = $( "#memo" ).val();
	postReq_ke( 'memo', { yyyy, mm, dd, memo }, data => {
		$( layer ).html( data );
		displayREC();
	});
}

// Koyomi Save Something
var koyomiSaveSome = ( yyyy, mm, dd, tdiv, id ) => {
	const some = $(`#${id}`).val();
	postReq_ke( 'some', { yyyy, mm, dd, tdiv, hh:99, some }, data => {
		$( layer ).html( data );
		displayREC();
	});
};

// Koyomi clear
var clearKoyomi = ( yyyy, mm, dd ) => {
	if( $( '#check_kc' ).is( ":checked" )){
		postReq_ke( 'clear', { yyyy, mm, dd }, data => {
			$( layer ).html( data );
			displayVIDEO( 'Cleared' );
		});
	}else{
		displayVIDEO( '(>_<)check!' );
	}
};

/////////////////////////////////////////////////////////////////////////////////////
var PhotoUpload = ( ymd ) => {
	const alt = document.getElementById( 'alt' ).value;
	const tdiv = document.getElementById( 'photo_tdiv' ).value;
	const origin = ymd + '-' + tdiv;

	form_data = new FormData( $( '#koyomi_puf' )[0] );
	form_data.append( 'command', 'photo_upload' );
	form_data.append( 'yyyy', '#{yyyy}' );
	form_data.append( 'mm', '#{mm}' );
	form_data.append( 'dd', '#{dd}' );
	form_data.append( 'tdiv', '#{tdiv}' );
	form_data.append( 'origin', origin );
	form_data.append( 'base', base );
	form_data.append( 'alt', alt );
	form_data.append( 'secure', '0' );

	$.ajax( "koyomi/koyomi-edit.cgi",
		{
			type: 'post',
			processData: false,
			contentType: false,
			data: form_data,
			dataype: 'html',
			success: function( data ){ $( layer ).html( data ); }
		}
	);
}

var photoMove = ( code, zidx ) => {
	postReq_ke( 'photo_mv', { origin:'#{ymd}-#{tdiv}', yyyy:'#{yyyy}', mm:'#{mm}', dd:'#{dd}', code, zidx, base }, data => {
		$( layer ).html( data );
	});
}

var photoDel = ( code ) => {
	postReq_ke( 'photo_del', { origin:'#{ymd}-#{tdiv}', yyyy:'#{yyyy}', mm:'#{mm}', dd:'#{dd}', code, base }, data => {
		$( layer ).html( data );
	});
}

</script>
JS

	puts js

end

puts '<br>(^q^)' if @debug