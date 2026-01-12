#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 koyomi food component 0.0.2 (2025/01/04)


#==============================================================================
#STATIC
#==============================================================================
@debug = false
script = File.basename( $0, '.cgi' )

#===============================================================================
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
		'title' 	=> "こよみ:食品構成",\
		'signpost'	=> "<img src='bootstrap-dist/icons/signpost.svg' style='height:2em; width:2em;'>",\
		'fromto'	=> "　～　",\
		'calc'		=> "計　算",\
		'no_day'	=> "該当日がありません",\
		'ew'		=> "予想g",\
		'sum'		=> "合計",\
		'period'	=> "期間総量（",\
		'days'		=> "日間）",\
		'fc'		=> "食品構成(g)",\
		'sg1'		=> "穀類",\
		'sg2'		=> "芋・でん粉類",\
		'sg3'		=> "砂糖・甘味類",\
		'sg4'		=> "豆類",\
		'sg5'		=> "種実類",\
		'sg6'		=> "野菜類",\
		'sg6gy'		=> "緑黄色野菜",\
		'sg6w'		=> "白色野菜",\
		'sg7'		=> "果実類",\
		'sg8'		=> "きのこ類",\
		'sg9'		=> "藻類",\
		'sg10'		=> "魚介類",\
		'sg11'		=> "肉類",\
		'sg12'		=> "卵類",\
		'sg13'		=> "乳類",\
		'sg13l'		=> "液体牛乳",\
		'sg13p'		=> "乳製品",\
		'sg14'		=> "油脂類",\
		'sg15'		=> "菓子類",\
		'sg16'		=> "嗜好飲料類",\
		'sg17'		=> "調味料・香辛料類",\
		'sg17mi'	=> "味噌",\
		'sg17ss'	=> "醤油",\
		'sg17sa'	=> "食塩",\
		'sg17o'		=> "その他",\
		'sg18'		=> "調理・流通食品",\
		'pfc'		=> "PFC比 (%)",\
		'others'	=> "その他",\
		'protein'	=> "たんぱく質(P)",\
		'fat'		=> "脂質(F)",\
		'carbon'	=> "炭水化物(C)",\
		'grain'		=> "穀類総エネルギー比(%)",\
		'proteina'	=> "動物性たんぱく質比(%)",\
		'average'	=> "1日平均",\
		'g100'		=> "100gあたり"
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


puts "Getting POST<br>" if @debug
command = @cgi['command']
yyyymmdds = @cgi['yyyymmdds']
yyyymmdde = @cgi['yyyymmdde']
ew_mode =  @cgi['ew_mode']
if @debug
	puts "command:#{command}<br>\n"
	puts "yyyymmdds:#{yyyymmdds}<br>\n"
	puts "yyyymmdde:#{yyyymmdde}<br>\n"
	puts "ew_mode:#{ew_mode}<br>\n"
	puts "<hr>\n"
end


puts 'LOAD config<br>' if @debug
r = db.query( "SELECT koyomi FROM #{$TB_CFG} WHERE user='#{user.name}';", false )
if r.first
	if r.first['koyomi'] != nil && r.first['koyomi'] != ''
		koyomi = JSON.parse( r.first['koyomi'] )
		if koyomi[script]
			yyyymmdds = koyomi[script]['yyyymmdds'] if yyyymmdds == '' || yyyymmdds == nil
			yyyymmdde = koyomi[script]['yyyymmdde'] if yyyymmdde == '' || yyyymmdde == nil
			ew_mode = koyomi[script]['ew_mode'] if ew_mode  == nil
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
palette.set_bit( @palette_default_name[1] )


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
				#fct_tdiv[c].load_fcz( 'fix', code )
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
				fct_total.set_food( food_nos, food_weights, false )
			end
		end
	end
end
puts "FCT calc<br>" if @debug
fct_total.calc
fct_total.digit


puts "Protein analysis<br>" if @debug
animal_protein = BigDecimal( 0 )
grain_energy = BigDecimal( 0 )
fct_total.fns.size.times do |c|
	fg = fct_total.fns[c].sub( /P|U/, '' ).slice( 0, 2 ).to_i
	#Animal protein
	animal_protein += fct_total.solid[c][1] if fg >= 10 && fg <= 13
	#Grains energy
	grain_energy += fct_total.solid[c][0] if fg == 1
end


puts "Sub group analysis<br>" if @debug
fch = {'00'=>0, '01'=>0, '02'=>0, '03'=>0, '04'=>0, '05'=>0, '06'=>0, '07'=>0, '08'=>0, '09'=>0, '10'=>0, '11'=>0, '12'=>0, '13'=>0, '14'=>0, '15'=>0, '16'=>0, '17'=>0, '18'=>0 }
wcv = 0
gycv = 0
milk_liquid = 0
milk_product = 0
salt = 0
miso = 0
shoyu = 0
seasoning = 0
fct_total.fns.size.times do |c|
	food_group = fct_total.fns[c].sub( /P|U/, '' ).slice( 0, 2 )
	fch[food_group] += fct_total.weights[c]

	case food_group
	when '00'
	when '06'
		puts "GYV<br>" if @debug
		r = db.query( "SELECT gycv FROM #{$TB_EXT} WHERE FN='#{fct_total.fns[c]}';", false )
		if r.first['gycv'] == 1
			gycv += fct_total.weights[c]
		else
			wcv += fct_total.weights[c]
		end
	when '13'
		puts "milk<br>" if @debug
		if ( fct_total.fns[c].to_i >= 13001 && fct_total.fns[c].to_i <= 13008 ) || fct_total.fns[c].to_i == 13059
			milk_liquid += fct_total.weights[c]
		else
			milk_product += fct_total.weights[c]
		end
	when '17'
		puts "seasoning<br>" if @debug
		if fct_total.fns[c].to_i >= 17019 && fct_total.fns[c].to_i <= 17025
			fct_total.weights[c] = fct_total.weights[c] / 100 * 1.0
		elsif fct_total.fns[c].to_i == 17026
			fct_total.weights[c] = fct_total.weights[c] / 100 * 2.5
		end

		salt_fns = %w( 17012 17013 17146 17147 17014 17089 )
		miso_fns = %w( 17044 17045 17046 17120 17147 17048 17119 17049 17050 17121 17122 17123 17124 )
		soysauce_fns = %w( 17007 17086 17008 17139 17009 17010 17011 17087 17088 )
 		if salt_fns.include?( fct_total.fns[c] )
			puts "salt<br>" if @debug
 			salt += fct_total.weights[c]

		elsif miso_fns.include?( fct_total.fns[c] )
			puts "miso<br>" if @debug
			miso += fct_total.weights[c]

		elsif soysauce_fns.include?( fct_total.fns[c] )
			puts "soy sauce<br>" if @debug
			shoyu += fct_total.weights[c]

		else
			puts "other<br>" if @debug
			seasoning += fct_total.weights[c]
		end
	end
end


puts 'Getting PFC rate<br>' if @debug
pfc = fct_total.calc_pfc


puts 'Animal protein rate<br>' if @debug
animal_protein_rate = ( animal_protein / fct_total.total[1] * 100 ).round( 1 )


puts 'Grain energy rate<br>' if @debug
grain_energy_rate = ( grain_energy / fct_total.total[0] * 100 ).round( 1 )


ew_checked = ''
ew_checked = 'CHECKED' if ew_mode == '1'

if day_count > 0
	compo_table = <<-"CT"
<table class="table table-bordered table-sm">
	<tbody>
	<tr><th width="20%" rowspan='24'>#{l['fc']}</th><th width="25%">#{l['sg1']}</th><td width="15%">#{fch['01'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg2']}</th><td>#{fch['02'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg3']}</th><td>#{fch['03'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg4']}</th><td>#{fch['04'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg5']}</th><td>#{fch['05'].round( 1 ).to_f}</td></tr>
	<tr><th rowspan="2">#{l['sg6']}</th><td rowspan="2">#{fch['06'].round( 1 ).to_f}</td><th width="25%">#{l['sg6gy']}</th><td>#{gycv.round( 1 ).to_f}</td></tr>
			<tr><th>#{l['sg6w']}</th><td>#{wcv.round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg7']}</th><td>#{fch['07'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg8']}</th><td>#{fch['08'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg9']}</th><td>#{fch['09'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg10']}</th><td>#{fch['10'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg11']}</th><td>#{fch['11'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg12']}</th><td>#{fch['12'].round( 1 ).to_f}</td></tr>
	<tr><th rowspan="2">#{l['sg13']}</th><td rowspan="2">#{fch['13'].round( 1 ).to_f}</td><th>#{l['sg13l']}</th><td>#{milk_liquid.round( 1 ).to_f}</td></tr>
			<tr><th>#{l['sg13p']}</th><td>#{milk_product.round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg14']}</th><td>#{fch['14'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg15']}</th><td>#{fch['15'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg16']}</th><td>#{fch['16'].round( 1 ).to_f}</td></tr>
	<tr><th rowspan="4">#{l['sg17']}</th><td rowspan="4">#{fch['17'].round( 1 ).to_f}</td><th>#{l['sg17mi']}</th><td>#{miso.round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17ss']}</th><td>#{shoyu.round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17sa']}</th><td>#{salt.round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17o']}</th><td>#{seasoning.round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg18']}</th><td>#{fch['18'].round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sum']}</th><td>#{fct_total.total_weight.round( 1 ).to_f}</td></tr>
	<tr><th rowspan='3'>#{l['pfc']}</th><th>#{l['protein']}</th><td>#{pfc[0].to_f}</td></tr>
		<th>#{l['fat']}</th><td>#{pfc[1].to_f}</td></tr>
		<th>#{l['carbon']}</th><td>#{pfc[2].to_f}</td></tr>
	<tr><th rowspan='2'>#{l['others']}</th><th>#{l['grain']}</th><td>#{grain_energy_rate.to_f}</td></tr>
		<th>#{l['proteina']}</th><td>#{animal_protein_rate.to_f}</td></tr>
	</tbody>
</table>
CT

	compo_ave_table = <<-"CAT"
<table class="table table-bordered table-sm">
	<tbody>
	<tr><th width="20%" rowspan='24'>#{l['fc']}</th><th width="25%">#{l['sg1']}</th><td width="15%">#{( fch['01'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg2']}</th><td>#{( fch['02'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg3']}</th><td>#{( fch['03'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg4']}</th><td>#{( fch['04'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg5']}</th><td>#{( fch['05'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th rowspan="2">#{l['sg6']}</th><td rowspan="2">#{( fch['06'] / day_count ).round( 1 ).to_f}</td><th width="25%">#{l['sg6gy']}</th><td>#{( gycv / day_count ).round( 1 ).to_f}</td></tr>
			<tr><th>#{l['sg6w']}</th><td>#{( wcv / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg7']}</th><td>#{( fch['07'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg8']}</th><td>#{( fch['08'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg9']}</th><td>#{( fch['09'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg10']}</th><td>#{( fch['10'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg11']}</th><td>#{(fch['11'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg12']}</th><td>#{(fch['12'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th rowspan="2">#{l['sg13']}</th><td rowspan="2">#{( fch['13'] / day_count ).round( 1 ).to_f}</td><th>#{l['sg13l']}</th><td>#{( milk_liquid / day_count ).round( 1 ).to_f}</td></tr>
			<tr><th>#{l['sg13p']}</th><td>#{( milk_product / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg14']}</th><td>#{( fch['14'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg15']}</th><td>#{( fch['15'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg16']}</th><td>#{( fch['16'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th rowspan="4">#{l['sg17']}</th><td rowspan="4">#{( fch['17'] / day_count ).round( 1 ).to_f}</td><th>#{l['sg17mi']}</th><td>#{( miso / day_count ).round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17ss']}</th><td>#{( shoyu / day_count ).round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17sa']}</th><td>#{( salt / day_count ).round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17o']}</th><td>#{( seasoning / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg18']}</th><td>#{( fch['18'] / day_count ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sum']}</th><td>#{( fct_total.total_weight / day_count ).round( 1 ).to_f}</td></tr>
	</tbody>
</table>
CAT

	t100 = fct_total.total_weight / 100
	compo_g100_table = <<-"CG100T"
<table class="table table-bordered table-sm">
	<tbody>
	<tr><th width="20%" rowspan='24'>#{l['fc']}</th><th width="25%">#{l['sg1']}</th><td width="15%">#{( fch['01'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg2']}</th><td>#{( fch['02'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg3']}</th><td>#{( fch['03'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg4']}</th><td>#{( fch['04'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg5']}</th><td>#{( fch['05'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th rowspan="2">#{l['sg6']}</th><td rowspan="2">#{( fch['06'] / t100 ).round( 1 ).to_f}</td><th width="25%">#{l['sg6gy']}</th><td>#{( gycv / t100 ).round( 1 ).to_f}</td></tr>
			<tr><th>#{l['sg6w']}</th><td>#{( wcv / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg7']}</th><td>#{( fch['07'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg8']}</th><td>#{( fch['08'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg9']}</th><td>#{( fch['09'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg10']}</th><td>#{( fch['10'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg11']}</th><td>#{( fch['11'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg12']}</th><td>#{( fch['12'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th rowspan="2">#{l['sg13']}</th><td rowspan="2">#{( fch['13'] / t100 ).round( 1 ).to_f}</td><th>#{l['sg13l']}</th><td>#{( milk_liquid / t100 ).round( 1 ).to_f}</td></tr>
			<tr><th>#{l['sg13p']}</th><td>#{( milk_product / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg14']}</th><td>#{( fch['14'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg15']}</th><td>#{( fch['15'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg16']}</th><td>#{( fch['16'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th rowspan="4">#{l['sg17']}</th><td rowspan="4">#{( fch['17'] / t100 ).round( 1 ).to_f}</td><th>#{l['sg17mi']}</th><td>#{( miso / t100 ).round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17ss']}</th><td>#{( shoyu / t100 ).round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17sa']}</th><td>#{( salt / t100 ).round( 1 ).to_f}</td></tr>
		<tr><th>#{l['sg17o']}</th><td>#{( seasoning / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sg18']}</th><td>#{( fch['18'] / t100 ).round( 1 ).to_f}</td></tr>
	<tr><th>#{l['sum']}</th><td>#{( fct_total.total_weight / t100 ).round( 1 ).to_f}</td></tr>
	</tbody>
</table>
CG100T

	day_ave = "<h5>#{l['average']}</h5>"
	g100 = "<h5>#{l['g100']}</h5>"
else
	compo_table = l['no_day']
	compo_ave_table = ''
	compo_g100_table = ''
	day_ave = ''
	g100 = ''
end


puts 'HTML <br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l['title']}</h5></div>
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
		<button class='btn btn-sm btn-info' onclick='calcKoyomiCompo()'>#{l['calc']}</buttnon>
	</div>
	<br>
	<h5>#{l['period']}#{day_count}#{l['days']}</h5>
	#{compo_table}
	#{day_ave}
	#{compo_ave_table}
	#{g100}
	#{compo_g100_table}
</div>

HTML

puts html


####
if command == 'compo'
		koyomi[script] = { 'yyyymmdds' => yyyymmdds, 'yyyymmdde' => yyyymmdde, 'ew_mode' => ew_mode }
		koyomi_ = JSON.generate( koyomi )
	db.query( "UPDATE #{$TB_CFG} SET koyomi='#{koyomi_}' WHERE user='#{user.name}';", true )
end
