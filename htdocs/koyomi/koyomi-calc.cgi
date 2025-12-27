#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 koyomi calc 0.0.5 (2025/07/01)


#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'
require '../brain'


#==============================================================================
#DEFINITION
#==============================================================================

#### Language_pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		'koyomi' 	=> "こよみ栄養計算",\
		'fromto'	=> "　～　",\
		'calc'		=> "計　算",\
		'no_day'	=> "該当日がありません",\
		'ew'		=> "予想g",\
		'name'		=> "栄養成分",\
		'unit'		=> "単位",\
		'volume'	=> "合計",\
		'breakfast'	=> "朝食",\
		'lunch'		=> "昼食",\
		'dinner'	=> "夕食",\
		'supply'	=> "捕食・間食",\
		'period'	=> "期間総量（",\
		'days'		=> "日間）",\
		'average'	=> "１日平均",\
		'ratio'		=> "割合",
		'fillr'		=> "充足率(%)",
		'reference'	=> "<img src='bootstrap-dist/icons/boxes.svg' style='height:1.2em; width:1.2em;'>参考値",
		'fcz'		=> "<img src='bootstrap-dist/icons/boxes.svg' style='height:1.5em; width:1.5em;'>",\
		'palette'	=> "<img src='bootstrap-dist/icons/palette.svg' style='height:1.5em; width:1.5em;'>"
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

#### Guild member check
if user.status < 3
	puts "Guild member error."
	exit
end


puts "Getting POST<br>" if @debug
command = @cgi['command']
yyyymmdds = @cgi['yyyymmdds']
yyyymmdde = @cgi['yyyymmdde']
palette_ = @cgi['palette']
ew_mode =  @cgi['ew_mode']
fcz = @cgi['fcz']
if @debug
	puts "command:#{command}<br>\n"
	puts "yyyymmdds:#{yyyymmdds}<br>\n"
	puts "yyyymmdde:#{yyyymmdde}<br>\n"
	puts "palette:#{palette_}<br>\n"
	puts "ew_mode:#{ew_mode}<br>\n"
	puts "<hr>\n"
end


puts 'LOAD config<br>' if @debug
r = db.query( "SELECT koyomi FROM #{$TB_CFG} WHERE user='#{user.name}';", false )
if r.first
	if r.first['koyomi'] != nil && r.first['koyomi'] != ''
		koyomi = JSON.parse( r.first['koyomi'] )
		if koyomi['calc']
			yyyymmdds = koyomi['calc']['yyyymmdds'] if yyyymmdds == '' || yyyymmdds == nil
			yyyymmdde = koyomi['calc']['yyyymmdde'] if yyyymmdde == '' || yyyymmdde == nil
			palette_ = koyomi['calc']['palette'] if palette_ == '' || palette_ == nil
			fcz = koyomi['calc']['fcz'] if fcz == '' || fcz == nil
			ew_mode = koyomi['calc']['ew_mode'] if ew_mode  == nil
		end
	end
end


puts "Multi calc process<br>" if @debug
day_list = []
koyomi_box = [ Hash.new, Hash.new, Hash.new, Hash.new ]
r = db.query( "SELECT * FROM #{$TB_KOYOMI} WHERE user='#{user.name}' AND tdiv != 4 AND date BETWEEN '#{yyyymmdds}' AND '#{yyyymmdde}';", false )
r.each do |e|
	koyomi_box[e['tdiv'].to_i][e['date'].to_s] = e['koyomi']
	day_list << e['date'].to_s
end
day_list.uniq!
day_count = day_list.size


puts "Palette setting<br>" if @debug
palette = Palette.new( user )
palette_ = @palette_default_name[0] if palette_ == nil || palette_ == '' || palette_ == '0'
palette.set_bit( palette_ )

puts 'HTMLパレットの生成 <br>' if @debug
palette_html = ''
palette.sets.each_key do |k|
	palette_html << "<option value='#{k}' #{$SELECT[palette_ == k]}>#{k}</option>"
end


puts 'HTML FCZの生成 <br>' if @debug
fcz_html = ''
r = db.query( "SELECT * FROM #{$TB_FCZ} WHERE user='#{user.name}' AND base='ref_intake';", false )
r.each do |e|
	fcz_html << "<option value='#{e['code']}' #{$SELECT[fcz == e['code']]}>#{e['name']}</option>"
end
r_fcz = db.query( "SELECT * FROM #{$TB_FCZ} WHERE user='#{user.name}' AND base='ref_intake' AND code='#{fcz}';", false )



fct_total = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
fct_total.load_palette( palette.bit )

fct_tdiv = []
4.times do |c|
	fct_tdiv[c] = FCT.new( user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
	fct_tdiv[c].load_palette( palette.bit )

	koyomi_box[c].each do |k, v|
		code_set = []
		rate_set = []
		unit_set = []

		puts 'Row<br>' if @debug
		a = []
		a = v.split( "\t" ) if v
		a.each do |e|
			koyomi_code, koyomi_rate, koyomi_unit = e.split( '~' )[0..2]
			code_set << koyomi_code
			rate_set << koyomi_rate
			unit_set << koyomi_unit
		end

		code_set.size.times do |cc|
			code = code_set[cc]
			rate = food_weight_check( rate_set[cc] ).last
			unit = unit_set[cc]

			if /\?/ =~ code
				fct_tdiv[c].into_zero
			elsif /\-z\-/ =~ code
				puts 'FIX<br>' if @debug
				fct_tdiv[c].load_fcz( 'fix', code )
			else
				puts 'Recipe<br>' if @debug
				recipe_codes = []
				if /\-m\-/ =~ code
					recipe_codes = menu2rc( user, code )
				else
					recipe_codes << code
				end

				food_nos = []
				food_weights = []
				recipe_codes.each do |e|
					if /\-r\-/ =~ e || /\w+\-\h{4}\-\h{4}/ =~ e
						fns, fws = recipe2fns( user, e, rate, unit, ew_mode )[0..1]
						food_nos.concat( fns )
						food_weights.concat( fws )
					else
						food_nos << code
						food_weights << unit_weight( rate, unit, code )
					end
				end

				puts 'Foods<br>' if @debug
				fct_tdiv[c].set_food( food_nos, food_weights, false )
			end
		end
	end

	puts 'Start calculation<br>' if @debug
	fct_tdiv[c].calc
	fct_tdiv[c].digit
	fct_total.into_solid( fct_tdiv[c].total )
end


puts "Summary html<br>" if @debug
fct_total.calc
fct_total.digit


fct_table = ''
fct_ave_table = ''
fct_rate_table = ''
fct_fillr_table = ''
if day_count >= 1
	# Sum
	fct_table << '<table class="table table-sm table-striped">'
	fct_table << '<tr>'
	fct_table << "<th width='30%' class='fct_item'>#{l['name']}</th>"
	fct_table << "<th width='10%' class='fct_item'>#{l['unit']}</th>"
	fct_table << "<th width='10%' class='fct_item'>#{l['volume']}</th>"
	fct_table << "<th width='10%' class='fct_item'>#{l['breakfast']}</th>"
	fct_table << "<th width='10%' class='fct_item'>#{l['lunch']}</th>"
	fct_table << "<th width='10%' class='fct_item'>#{l['dinner']}</th>"
	fct_table << "<th width='10%' class='fct_item'>#{l['supply']}</th>"
	fct_table << '</tr>'

	fct_total.names.size.times do |i|
		fct_table << '<tr>'
		fct_table << "<td>#{fct_total.names[i]}</td>"
		fct_table << "<td>#{fct_total.units[i]}</td>"
		fct_table << "<td>#{fct_total.total[i]}</td>"
		fct_table << "<td>#{fct_tdiv[0].total[i]}</td>"
		fct_table << "<td>#{fct_tdiv[1].total[i]}</td>"
		fct_table << "<td>#{fct_tdiv[2].total[i]}</td>"
		fct_table << "<td>#{fct_tdiv[3].total[i]}</td>"
		fct_table << '</tr>'
	end
	fct_table << '</table>'

	# Average
	fct_ave_table << '<table class="table table-sm table-striped">'
	fct_ave_table << '<tr>'
	fct_ave_table << "<th width='30%' class='fct_item'>#{l['name']}</th>"
	fct_ave_table << "<th width='10%' class='fct_item'>#{l['unit']}</th>"
	fct_ave_table << "<th width='10%' class='fct_item'>#{l['volume']}</th>"
	fct_ave_table << "<th width='10%' class='fct_item'>#{l['breakfast']}</th>"
	fct_ave_table << "<th width='10%' class='fct_item'>#{l['lunch']}</th>"
	fct_ave_table << "<th width='10%' class='fct_item'>#{l['dinner']}</th>"
	fct_ave_table << "<th width='10%' class='fct_item'>#{l['supply']}</th>"
	fct_ave_table << '</tr>'

	fct_total.names.size.times do |i|
		fct_ave_table << '<tr>'
		fct_ave_table << "<td>#{fct_total.names[i]}</td>"
		fct_ave_table << "<td>#{fct_total.units[i]}</td>"
		fct_ave_table << "<td>#{( fct_total.total[i] / day_count ).round( fct_total.frcts[i] )}</td>"
		fct_ave_table << "<td>#{( fct_tdiv[0].total[i] / day_count ).round( fct_tdiv[0].frcts[i] )}</td>"
		fct_ave_table << "<td>#{( fct_tdiv[1].total[i] / day_count ).round( fct_tdiv[1].frcts[i] )}</td>"
		fct_ave_table << "<td>#{( fct_tdiv[2].total[i] / day_count ).round( fct_tdiv[2].frcts[i] )}</td>"
		fct_ave_table << "<td>#{( fct_tdiv[3].total[i] / day_count ).round( fct_tdiv[3].frcts[i] )}</td>"
		fct_ave_table << '</tr>'
	end
	fct_ave_table << '</table>'

	# Ratio
	fct_rate_table << '<table class="table table-sm table-striped">'
	fct_rate_table << '<tr>'
	fct_rate_table << "<th width='30%' class='fct_item'>#{l['name']}</th>"
	fct_rate_table << "<th width='10%' class='fct_item'>#{l['unit']}</th>"
	fct_rate_table << "<th width='10%' class='fct_item'>#{l['volume']}</th>"
	fct_rate_table << "<th width='10%' class='fct_item'>#{l['breakfast']}</th>"
	fct_rate_table << "<th width='10%' class='fct_item'>#{l['lunch']}</th>"
	fct_rate_table << "<th width='10%' class='fct_item'>#{l['dinner']}</th>"
	fct_rate_table << "<th width='10%' class='fct_item'>#{l['supply']}</th>"
	fct_rate_table << '</tr>'

	fct_total.names.size.times do |i|
		t = fct_total.total[i]
		if t == 0
			total = '-'
			breakfast = '-'
			lunch = '-'
			dinner = '-'
			supply = '-'
		else
			total = ( t / t * 100 ).to_f.round( 1 )
			breakfast = ( fct_tdiv[0].total[i].to_f / t * 100 ).round( 1 )
			lunch = ( fct_tdiv[1].total[i].to_f / t * 100 ).round( 1 )
			dinner = ( fct_tdiv[2].total[i].to_f / t * 100 ).round( 1 )
			supply = ( fct_tdiv[3].total[i].to_f / t * 100 ).round( 1 )
		end


		fct_rate_table << '<tr>'
		fct_rate_table << "<td>#{fct_total.names[i]}</td>"
		fct_rate_table << "<td>%</td>"
		fct_rate_table << "<td>#{total}</td>"
		fct_rate_table << "<td>#{breakfast}</td>"
		fct_rate_table << "<td>#{lunch}</td>"
		fct_rate_table << "<td>#{dinner}</td>"
		fct_rate_table << "<td>#{supply}</td>"
		fct_rate_table << '</tr>'
	end
	fct_rate_table << '</table>'

	# Fill rate
	fct_fillr_table << '<table class="table table-sm table-striped">'
	fct_fillr_table << '<tr>'
	fct_fillr_table << "<th width='30%' class='fct_item'>#{l['name']}</th>"
	fct_fillr_table << "<th width='10%' class='fct_item'>#{l['unit']}</th>"
	fct_fillr_table << "<th width='10%' class='fct_item'>#{l['fillr']}</th>"
	fct_fillr_table << "<th width='10%' class='fct_item'>#{l['average']}</th>"
	fct_fillr_table << "<th width='10%' class='fct_item'>#{l['reference']}</th>"
	fct_fillr_table << "<th width='10%' class='fct_item'></th>"
	fct_fillr_table << "<th width='10%' class='fct_item'></th>"
	fct_fillr_table << '</tr>'

	fct_total.names.size.times do |i|
		t = fct_total.total[i]
		if t == 0 || r_fcz.first == nil
			total = '-'
			fillr = '-'
			reference = '-'
		else
			total = ( fct_total.total[i] / day_count ).round( fct_total.frcts[i] )
			reference = r_fcz.first[fct_total.items[i]].to_f.round( 1 )
			if reference != nil && reference != ''
				fillr = ( total / reference.to_f * 100 ).round( 1 )
			else
				reference = '-'
				fillr = '-'
			end

			fct_fillr_table << '<tr>'
			fct_fillr_table << "<td>#{fct_total.names[i]}</td>"
			fct_fillr_table << "<td>#{fct_total.units[i]}</td>"
			fct_fillr_table << "<td>#{fillr}</td>"
			fct_fillr_table << "<td>#{total}</td>"
			fct_fillr_table << "<td>#{reference}</td>"
			fct_fillr_table << "<td></td>"
			fct_fillr_table << "<td></td>"
			fct_fillr_table << '</tr>'
		end
	end
	fct_fillr_table << '</table>'




	day_ave = "<h5>#{l['average']}</h5>"
	day_ratio = "<h5>#{l['ratio']}</h5>"
	day_fillr = "<h5>#{l['fillr']}</h5>"
else
	fct_table << "<h5>#{l['no_day']}</h5>"
	day_ave = ''
	day_ratio = ''
	day_fillr = ''
end


ew_checked = ''
ew_checked = 'CHECKED' if ew_mode == '1'


puts "HTML process<br>" if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-2'><h5>#{l['koyomi']}</h5></div>
	</div>
	<div class='row'>
		<div class='col-2 form-inline'>
			<input type='date' class='form-control form-control-sm' id='yyyymmdds' value='#{yyyymmdds}'>
		</div>
		<div align='center' class='col-1'>
			#{l['fromto']}
		</div>
		<div class='col-2 form-inline'>
			<input type='date' class='form-control form-control-sm' id='yyyymmdde' value='#{yyyymmdde}'>
		</div>
		<div class='col-1'></div>
		<div class='col-1 form-check'>
			<input class="form-check-input" type="checkbox" id="ew_mode" #{ew_checked}>
			<label class="form-check-label">#{l['ew']}</label>
		</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-3'>
			<div class="input-group input-group-sm">
				<label class="input-group-text">#{l['palette']}</label>
				<select class="form-select form-select-sm" id="palette">
					#{palette_html}
				</select>
			</div>
		</div>
		<div class='col-4'>
			<div class="input-group input-group-sm">
				<label class="input-group-text">#{l['fcz']}</label>
				<select class="form-select form-select-sm" id="fcz">
					#{fcz_html}
				</select>
			</div>

		</div>
	</div>
	<br>

	<div class='row'>
		<button class='btn btn-sm btn-info' onclick='calcKoyomiCalc()'>#{l['calc']}</buttnon>
	</div>
	<br>
	<h5>#{l['period']}#{day_count}#{l['days']}</h5>
	#{fct_table}
	#{day_ave}
	#{fct_ave_table}
	#{day_ratio}
	#{fct_rate_table}
	#{day_fillr}
	#{fct_fillr_table}
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================

if command == 'calc'
		koyomi['calc'] = { 'yyyymmdds' => yyyymmdds, 'yyyymmdde' => yyyymmdde, 'palette' => palette_, 'fcz' => fcz, 'ew_mode' => ew_mode }
		koyomi_ = JSON.generate( koyomi )
	db.query( "UPDATE #{$TB_CFG} SET koyomi='#{koyomi_}' WHERE user='#{user.name}';", true )
end


#==============================================================================
#FRONT SCRIPT
#==============================================================================

if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

// Calculation
var calcKoyomiCalc = () => {
	var palette = document.getElementById( "palette" ).value;
	var fcz = document.getElementById( "fcz" ).value;
	var yyyymmdds = document.getElementById( "yyyymmdds" ).value;
	var yyyymmdde = document.getElementById( "yyyymmdde" ).value;
	var ew_mode = document.getElementById("ew_mode").checked ? 1 : 0;

	postLayer( kp + '#{myself}', 'calc', true, 'L1',
		{ palette, fcz, yyyymmdds, yyyymmdde, ew_mode }
	);
};

</script>
JS

	puts js
end

puts '<br>(^q^)' if @debug
