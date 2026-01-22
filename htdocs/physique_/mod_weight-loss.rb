# Weight loss module for Physique 0.4.1 (2025/12/27)
#encoding: utf-8

@period = 96

def physique_module( cgi, db )
	l = module_lp( db.user.language )
	mod = cgi['mod']
	today_p = Time.parse( @datetime )

	puts "LOAD bio config<br>" if @debug
	res = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user=?", false, [db.user.name] )&.first
	unless res['bio'].to_s.empty?
		bio = JSON.parse( res['bio'] )
		sex = bio['sex'].to_i
		birth = Time.parse( bio['birth'] )
		height = bio['height'].to_f * 100
		weight = bio['weight'].to_f
		pgene = bio['pgene'].to_i
		age = ( Date.today.strftime( "%Y%m%d" ).to_i - birth.strftime( "%Y%m%d" ).to_i ) / 10000
	end

	if height.nil? || weight.nil? || age.nil?
		puts l[:error_no_set]
		exit( 0 )
	end


	puts "LOAD config JSON<br>" if @debug
	cfg_lw = Config.new( db.user, 'weight-loss' )
	start_date = cgi['start_date']
	pal = cgi['pal'].to_f
	eenergy = cgi['eenergy'].to_i
	if pal == 0.0 || eenergy == 0
		start_date = cfg_lw.value( 'start_date' ).nil? ? $DATE : cfg_lw.value( 'start_date' )
		pal = cfg_lw.value( 'pal' ).nil? ? 1.5 : cfg_lw.value( 'pal' ).to_f
		eenergy = cfg_lw.value( 'eenergy' ).nil? ? calc_energy( weight, height, age, sex, pal ) : cfg_lw.value( 'eenergy' ).to_i
	end


	html_module = ''
	case cgi['step']
	when 'form'
		sex_ = [l[:male], l[:female]]

		html_module = <<~"HTML"
			<div class='row'>
				<div class='col'><h5>#{l[:chart_name]}</h5></div>
			</div>

			<div class='row'>
			<div class='col-6'>
			<table class='table table-sm'>
				<thead><th></th><th>#{l[:sex]}</th><th>#{l[:age]}</th><th>#{l[:height]}</th><th>#{l[:weight]}</th></thead>
				<tr><td></td><td>#{sex_[sex]}</td><td>#{age}</td><td>#{height}</td><td>#{weight}</td></tr>
			</table>
			</div>
			</div>

			<div class='row'>
				<div class='col'>
					<div class='input-group input-group-sm'>
						<span class='input-group-text'>#{l[:start_date]}</span>
						<input type='date' class='form-control' id='start_date' value='#{start_date}' onchange='WeightLossChartDraw()'>
					</div>
				</div>
				<div class='col'>
					<div class="input-group input-group-sm">
						<label class="input-group-text">#{l[:pal]}</label>
						<input type='number' min='0.5' max='2.5' step='0.05' class='form-control' id='pal' value='#{pal}' onchange='WeightLossChartDraw()'>
					</div>
				</div>

				<div class='col'>
					<div class='input-group input-group-sm'>
						<span class='input-group-text'>#{l[:eenergy]}</span>
						<input type='number' class='form-control' id='eenergy' min='0' value='#{eenergy}' onchange='WeightLossChartDraw()'>
					</div>
				</div>
			</div>
		HTML

########
		####

	when 'raw'
		puts "SET date<br>" if @debug

		start_date_p = Time.parse( start_date )
		end_date = ( start_date_p + ( @period - 1 ) * 86400 ).strftime( "%Y-%m-%d" )
		p start_date, end_date if @debug


		puts "SET X axis<br>" if @debug
		x_day = []
		start_date_p = Time.parse( start_date )
		@period.times do |c|
			x_day[c] = start_date_p.strftime( "%Y-%m-%d" )
			start_date_p += 86400
		end


		puts "SET measured weight & delta energy<br>" if @debug
		measured = []
		denergy = []
		start_date_p = Time.parse( start_date )
		r = db.query( "SELECT * FROM #{$TB_KOYOMIEX} WHERE user=? AND date BETWEEN ? AND ?", false, [db.user.name, start_date, end_date] )
		r.each do |e|
			if e['cell'] != nil
				kexc = JSON.parse( e['cell'] )
				day_pass = (( Time.parse( e['date'].strftime( "%Y-%m-%d" )) - start_date_p ) / 86400 ).to_i
				measured[day_pass] = kexc['体重'].to_f if kexc['体重'] != nil
				denergy[day_pass] = kexc['Δエネルギー'].to_f if kexc['Δエネルギー'] != nil
			end
		end


		puts "Day 4 stable weight<br>" if @debug
		d4sw = []
		if measured.size >= 1
			start_day_p = Time.parse( start_date )
			skip = 0
			@period.times do |c|
				break if start_day_p > today_p
				if measured[c] != nil && measured[c] != '' && measured[c] != 0
					case skip
					when 0
						d4sw[c] = measured[c]
						skip = 1
					when 1
						d4sw[c] = ( measured[c] + ( measured[c-1] / 2 )) / 1.5
						skip = 2
					when 2
						d4sw[c] = ( measured[c] + ( measured[c-1] / 2 ) + ( measured[c-2] / 4 )) / 1.75
						skip = c
					else
						d4sw[c] = ( measured[c] + ( measured[c-1] / 2 ) + ( measured[c-2] / 4 ) + ( measured[c-3] / 8 )) / 1.875
						skip = c
					end
				else
					d4sw[c] = nil
					skip = 0
				end

				start_day_p += 86400
			end
  		d4sw.map! { |x| x.nil? ? 'NA' : x.round( 2 ) }

		end

		puts "LOAD Intake enargy 1pass<br>" if @debug
		tdiv_enargy = [[],[],[],[]]
		start_date_p = Time.parse( start_date )

		puts "Palette setting<br>" if @debug
		palette = Palette.new( db.user )
		palette.set_bit( @palette_default_name.first )

		puts "Koyomi config<br>" if @debug
		koyomi = Koyomi.new( db.user )
		koyomi.load_db( start_date, end_date )

		fct_tdiv = FCT.new( db.user, @fct_item, @fct_name, @fct_unit, @fct_frct, 1, 1 )
		fct_tdiv.load_palette( palette.bit )

		koyomi.fz_bit.each do |date, fz_bit|
			day_pass = (( Time.parse( date ) - start_date_p ) / 86400 ).to_i
			4.times do |tdiv|
				if fz_bit[tdiv] == 1
					if /^\?\-\-/ =~ koyomi.solid[date][tdiv]
						tdiv_enargy[tdiv][day_pass] = '?--'
					elsif /^\?\-/ =~ koyomi.solid[date][tdiv]
						tdiv_enargy[tdiv][day_pass] = '?-'
					elsif /^\?\=/ =~ koyomi.solid[date][tdiv]
						tdiv_enargy[tdiv][day_pass] = '?='
					elsif /^\?\+\+/ =~ koyomi.solid[date][tdiv]
						tdiv_enargy[tdiv][day_pass] = '?++'
					elsif /^\?\+/ =~ koyomi.solid[date][tdiv]
						tdiv_enargy[tdiv][day_pass] = '?+'
					elsif /^\?0/ =~ koyomi.solid[date][tdiv]
						tdiv_enargy[tdiv][day_pass] = ''
					else
						fct_tdiv.flash()
						fct_tdiv.load_fcz( 'freeze', koyomi.fz_code[date][tdiv] )
						fct_tdiv.calc()
						tdiv_enargy[tdiv][day_pass] = fct_tdiv.pickt( 'ENERC_KCAL' ).to_i
					end
				end
			end
		end


		puts "SET tdiv energy / pahse<br>" if @debug
		tdiv_pset = Array.new( 4 ){ Array.new( 4 ){ [] }}
		0.upto( 3 ) do |tdiv|
			@period.times do |c|
				if /\d/ =~ tdiv_enargy[tdiv][c].to_s
					phase = ( c / 24 ).to_i
					tdiv_pset[phase][tdiv] << tdiv_enargy[tdiv][c].to_i
				end
			end
		end

		puts "SET tdiv average & SE / phase<br>" if @debug
		phase_energy_ave = Array.new( 4 ){ Array.new( 4, 0) }
		phase_energy_std = Array.new( 4 ){ Array.new( 4, 0) }
		0.upto( 3 ) do |phase|
			0.upto( 3 ) do |tdiv|
				values = tdiv_pset[phase][tdiv]
				if values.size > 0
					phase_energy_ave[phase][tdiv] = BigDecimal(  values.sum ) / values.size
					a = values.map do |x| ( x - phase_energy_ave[phase][tdiv] )**2 end
					phase_energy_std[phase][tdiv] = Math.sqrt( a.sum / a.size )
				end
			end
		end

		puts "CALC intake enargy 2pass<br>" if @debug
		ienergy = []
		0.upto( 3 ) do |tdiv|
			start_day_p = Time.parse( start_date )
			@period.times do |c|
				break if start_day_p > today_p
    		ienergy[c] ||= 0
				phase = ( c / 24 ).to_i

				tdiv_enargy[tdiv][c] = '' if tdiv_enargy[tdiv][c] == nil && tdiv == 3
				tdiv_enargy[tdiv][c] = '?=' if tdiv_enargy[tdiv][c] == nil
				ave = phase_energy_ave[phase][tdiv]
				std = phase_energy_std[phase][tdiv]

				case tdiv_enargy[tdiv][c].to_s
				when '?--'
					tdiv_enargy[tdiv][c] = ave - std
				when '?-'
					tdiv_enargy[tdiv][c] = ave - std / 2
				when '?='
					tdiv_enargy[tdiv][c] = ave
				when '?+'
					tdiv_enargy[tdiv][c] = ave + std / 2
				when '?++'
					tdiv_enargy[tdiv][c] = ave + std
				when ''
					tdiv_enargy[tdiv][c] = 0
				end
				ienergy[c] += tdiv_enargy[tdiv][c].to_i
				start_day_p += 86400
			end
		end

		puts "CALC actual enargy (intake + delta )<br>" if @debug
		aenergy = []
		acutual_phase_day = [0, 0, 0 ,0]
		acutual_phase_total = [0, 0, 0 ,0]
		start_day_p = Time.parse( start_date )
		@period.times do |c|
			break if start_day_p > today_p
			phase = ( c / 24 ).to_i
			denergy[c] = 0 if denergy[c] == nil
			if ienergy[c] == nil
				aenergy[c] = denergy[c]
			else
				aenergy[c] = ienergy[c] + denergy[c]
			end
			acutual_phase_day[phase] += 1
			acutual_phase_total[phase] += aenergy[c]
			start_day_p += 86400
		end

		puts "CALC actual average / phase<br>" if @debug
		ave_energy = [0, 0, 0 ,0]
		0.upto( 3 ) do |phase|
			ave_energy[phase] = ( acutual_phase_total[phase] / acutual_phase_day[phase] ).to_i if acutual_phase_day[phase] != 0
			ave_energy[phase] = l[:empty] if ave_energy[phase] == 0
		end

		puts "SET Guide weight<br>" if @debug
		guide = []
		guide[0] = measured[0] || weight
		@period.times do |c|
			cenergy = calc_energy( guide[c - 1], height, age, sex, pal )
			guide[c] = ( guide[0] - (( cenergy.to_f - eenergy.to_f ) / 7200 * c ))
		end
		guide.map! do |x| x.round( 2 ) end

		#Theoletical weight
		theoletic = []
		theoletic[0] = measured[0] || weight
		start_day_p = Time.parse( start_date ) + 86400
		1.upto( @period - 1 ) do |c|
			break if start_day_p > today_p
			cenergy = calc_energy( theoletic[c - 1], height, age, sex, pal )
			theoletic[c] = ( theoletic[c - 1] - (( cenergy.to_f - aenergy[c] ) / 7200 ))
			start_day_p += 86400
		end
		theoletic.map! do |x| x.round( 2 ) end

		raw = []
		raw[0] = x_day.unshift( 'x_day' ).join( ',' )
		raw[1] = guide.unshift( l[:data_guide] ).join( ',' )
		raw[2] = theoletic.unshift( l[:data_theoletic] ).join( ',' )
		raw[3] = d4sw.unshift( l[:data_d4sw] ).join( ',' )
		raw[4] = ienergy.unshift( l[:data_ienergy] ).join( ',' )
		raw[5] = denergy.unshift( l[:data_denergy] ).join( ',' )
		raw[6] = aenergy.unshift( l[:data_aenergy] ).join( ',' )
		raw[7] = ave_energy.join( ',' )
		puts raw.join( ':' )

		cfg_lw.set_value( 'pal', pal )
		cfg_lw.set_value( 'eenergy', eenergy )
		cfg_lw.set_value( 'start_date', start_date )
		cfg_lw.update

		exit

	when 'results'
		html_module = '<div class="row">'
		html_module << "<div class='col'><div id='physique_#{mod}-chart' align='center'></div>"
		html_module << '</div>'
		html_module << js_chart( mod, l )

	when 'notice'
		html_module = <<~HTML
<h5>#{l[:bw_name]}</h5>
<div class="row">
  <div class="col">
    <div class="input-group input-group-sm">
      <span class="input-group-text">1st phase</span>
      <input type="text" class="form-control form-control-sm" id="aveep1" value="" disabled>
    </div>
  </div>
  <div class="col">
    <div class="input-group input-group-sm">
      <span class="input-group-text">2nd phase</span>
      <input type="text" class="form-control form-control-sm" id="aveep2" value="" disabled>
    </div>
  </div>
  <div class="col">
    <div class="input-group input-group-sm">
      <span class="input-group-text">3rd phase</span>
      <input type="text" class="form-control form-control-sm" id="aveep3" value="" disabled>
    </div>
  </div>
  <div class="col">
    <div class="input-group input-group-sm">
      <span class="input-group-text">final phase</span>
      <input type="text" class="form-control form-control-sm" id="aveep4" value="" disabled>
    </div>
  </div>
</div>
HTML
	end

	return html_module
end


def calc_energy( weight, height, age, sex, pal )
	result = 0
	if sex == 0
		result = (( 0.0481 * weight + 0.0234 * height - 0.0138 * age - 0.4235 ) * 1000 / 4.186 )
	else
		result = (( 0.0481 * weight + 0.0234 * height - 0.0138 * age - 0.9708 ) * 1000 / 4.186 )
	end
	eer_result = ( result * pal )

	return eer_result
end


def js_chart( mod, l )
	js = <<-"JS"
<script type='text/javascript'>

var mod = '#{mod}';
var labels = {
  data_guide: '#{l[:data_guide]}',
  data_theoletic: '#{l[:data_theoletic]}',
  data_d4sw: '#{l[:data_d4sw]}',
  data_ienergy: '#{l[:data_ienergy]}',
  data_denergy: '#{l[:data_denergy]}',
  data_aenergy: '#{l[:data_aenergy]}',
  label_weight: '#{l[:label_weight]}',
  label_energy: '#{l[:label_energy]}',
};

// WeightLossChartDraw関数
var WeightLossChartDraw = async () => {
	dl3 = true;
//	dlf = true;
	displayBW();

	// フォーム入力値の取得
	const startDate = document.getElementById( 'start_date' ).value;
	const pal = document.getElementById( 'pal' ).value;
	const eenergy = document.getElementById( 'eenergy' ).value;

	try {
    // physique.cgiへのPOSTリクエスト（rawデータ取得）
		const rawResponse = await fetch( 'physique.cgi', {
			method: 'POST',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			body: new URLSearchParams({
				mod,
				step: 'raw',
				start_date: startDate,
				pal,
				eenergy,
			}),
		});

		if ( !rawResponse.ok ) throw new Error( 'Rawデータ取得に失敗' );

		const raw = await rawResponse.text();
		const columns = raw.split( ':' );

		// C3.jsチャート生成
		c3.generate({
			bindto: `#physique_${mod}-chart`,
			data: {
				columns: [
					columns[0].split(','), // x_day
					columns[1].split(','), // ガイド体重
					columns[2].split(','), // 理論体重
					columns[3].split(','), // D4安定体重
					columns[4].split(','), // 摂取エネルギー
					columns[5].split(','), // Δ消費エネルギー
					columns[6].split(','), // 実エネルギー
				],
				x: 'x_day',
				axes: {
					[labels.data_ienergy]: 'y2',
					[labels.data_denergy]: 'y2',
					[labels.data_aenergy]: 'y2',
				},
				labels: false,
				type: 'line',
				types: {
					[labels.data_ienergy]: 'area-step',
					[labels.data_denergy]: 'area-step',
					[labels.data_aenergy]: 'area-step',
				},
				colors: {
					[labels.data_guide]: '#d3d3d3',
					[labels.data_theoletic]: '#228b22',
					[labels.data_d4sw]: '#dc143c',
					[labels.data_ienergy]: '#ffd700',
					[labels.data_denergy]: '#00ffff',
					[labels.data_aenergy]: '#d2691e',
				},
				regions: {
					[labels.data_guide]: { start: 0, style: 'dashed' },
				},
			},
			axis: {
				x: { type: 'timeseries' },
				y: {
					type: 'linear',
					padding: { top: 50, bottom: 100 },
					label: { text: labels.label_weight, position: 'outer-middle' },
				},
				y2: {
					show: true,
					type: 'linear',
					padding: { top: 400, bottom: 0 },
					label: { text: labels.label_energy, position: 'outer-middle' },
				},
			},
			legend: { show: true, position: 'bottom' },
			line: { connectNull: true, step: { type: 'step' }},
			bar: { width: { ratio: 1.0 }},
			point: { show: true, r: 2 },
		});

		// 平均エネルギー値の処理
		const averageEnergies = columns[7].split(',');

		// physique.cgiへのPOSTリクエスト（noticeデータ取得）
		const noticeResponse = await fetch('physique.cgi', {
			method: 'POST',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			body: new URLSearchParams({ mod, step: 'notice' }),
		});

	    if ( !noticeResponse.ok ) throw new Error( 'Noticeデータ取得に失敗' );

		const noticeData = await noticeResponse.text();
		document.getElementById( 'L3' ).innerHTML = noticeData;
		document.getElementById( 'aveep1' ).value = averageEnergies[0];
		document.getElementById( 'aveep2' ).value = averageEnergies[1];
		document.getElementById( 'aveep3' ).value = averageEnergies[2];
		document.getElementById( 'aveep4' ).value = averageEnergies[3];
	} catch ( error ) {
	    console.error( 'エラー:', error );
	    // エラーメッセージをUIに表示する処理を追加可能
	}
};

WeightLossChartDraw();

</script>
JS

	return js
end


def module_lp( language )
	l = Hash.new
	l['ja'] = {
		mod_name:	"減量チャート",\
		male:  "男性",\
		female:  "女性",\
		chart_name:  "減量チャート",\
		sex:  "代謝的性別",\
		age:  "年齢",\
		height:  "身長（cm）",\
		weight:  "初期体重（kg）",\
		start_date:  "開始日",\
		pal:  "平均身体活動レベル",\
		eenergy:  "摂取予定エネルギー（kcal）",\
		data_ienergy:  "摂取エネルギー",\
		data_denergy:  "Δ消費エネルギー",\
		data_aenergy:  "実エネルギー",\
		data_guide:  "ガイド体重",\
		data_theoletic:  "理論体重",\
		data_d4sw:  "D4安定体重",\
		label_weight:  "体重 (kg)",\
		label_energy:  "エネルギー (kcal)",\
		empty:  "ごんぶと",\
		bw_name:  "平均摂取エネルギー",\
		error_no_set:  "設定から生体情報を設定してください。"
	}

	return l[language]
end
