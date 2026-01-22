# Weight keep module for Physique 0.1.1 (2025/07/02)
#encoding: utf-8

@debug = false

def physique_module( cgi, db )
	l = module_lp( db.user.language )
	mod = cgi['mod']
	today_p = Time.parse( @datetime )

	puts "LOAD bio config<br>" if @debug
	res = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user=?", false, [db.user.name] )&.first
	if res
		unless res['bio'].to_s.empty?
			bio = JSON.parse( res['bio'] )
			sex = bio['sex'].to_i
			birth = Time.parse( bio['birth'] )
			height = bio['height'].to_f * 100
			weight = bio['weight'].to_f
			pgene = bio['pgene'].to_i
			age = ( Date.today.strftime( "%Y%m%d" ).to_i - birth.strftime( "%Y%m%d" ).to_i ) / 10000
		end
	end

	if height.nil? || weight.nil? || age.nil?
		puts l[:error_no_set]
		exit( 0 )
	end


	puts "LOAD koyomi config<br>" if @debug
	res = db.query( "SELECT koyomi FROM #{$TB_CFG} WHERE user=?", false, [db.user.name] )&.first
	koyomi_start = @date
	if res
		unless res['koyomi'].to_s.empty?
			koyomi = JSON.parse( res['koyomi'] )
			koyomi_start = "#{koyomi['start']}" unless koyomi['start'].nil?
		end
	end


	puts "LOAD config JSON<br>" if @debug
	cfg_kw = Config.new( db.user, 'weight-keep' )
	start_date = cgi['start_date']
	pal = cgi['pal'].to_f
	keep = cgi['keep'].to_i
	if pal == 0.0 || keep == 0
		pal = cfg_kw.value( 'pal' ).nil? ? 1.5 : cfg_kw.value( 'pal' ).to_f
		keep = cfg_kw.value( 'keep' ).nil? ? weight : cfg_kw.value( 'keep' ).to_i
		start_date = cfg_kw.value( 'start_date' ).nil? ? koyomi_start : cfg_kw.value( 'start_date' )
		start_date = koyomi_start if start_date < koyomi_start
	end

	html_module = ''
	puts cgi['step'] if @debug
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
			<thead><th></th><th>#{l[:sex]}</th><th>#{l[:age]}</th><th>#{l[:height]}</th></thead>
			<tr><td></td><td>#{sex_[sex]}</td><td>#{age}</td><td>#{height}</td></tr>
		</table>
		</div>
		</div>

		<div class='row'>
			<div class='col'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>#{l[:start_date]}</span>
					<input type='date' class='form-control' id='start_date' value='#{start_date}' onchange='WeightKeepChartDraw()'>
				</div>
			</div>
			<div class='col'>
				<div class="input-group input-group-sm">
					<label class="input-group-text">#{l[:pal]}</label>
					<input type='number' min='0.5' max='2.5' step='0.05' class='form-control' id='pal' value='#{pal}' onchange='noticeEER()'>
				</div>
			</div>
			<div class='col'>
				<div class="input-group input-group-sm">
					<label class="input-group-text">#{l[:weight]}</label>
					<input type='number' min='30' max='300' step='1' class='form-control' id='keep' value='#{keep}' onchange='noticeEER()'>
				</div>
			</div>
		</div>
		HTML

	when 'raw'
		puts "SET date<br>" if @debug

		start_date_p = Time.parse( start_date )
		p start_date if @debug

		puts "SET X axis<br>" if @debug
		x_day = []
		start_date_p = Time.parse( start_date )
		while start_date_p <= today_p do
			x_day << start_date_p.strftime( "%Y-%m-%d" )
			start_date_p += 86400
		end

		puts "SET measured weight & body fat tate<br>" if @debug
		measured_weight = []
		bfr = []
		recent_weight = 0.0
		start_date_p = Time.parse( start_date )

		r = db.query( "SELECT * FROM #{$TB_KOYOMIEX} WHERE user=? AND date>=?", false, [db.user.name, start_date] )
		r.each do |e|
			if e['cell'] != nil
				kexc = JSON.parse( e['cell'] )
				day_pass = (( Time.parse( e['date'].strftime( "%Y-%m-%d" ) ) - start_date_p ) / 86400 ).to_i
				measured_weight[day_pass] = kexc['体重'].to_f if kexc['体重'] != nil
				recent_weight = kexc['体重'].to_f if kexc['体重'] != nil
				bfr[day_pass] = kexc['体脂肪率'].to_f if kexc['体脂肪率'] != nil
			end
		end

		measured_weight.map! { |x| ( x.nil? || x == 0 ) ? 'NA' : x }
		bfr.map! { |x| ( x.nil? || x == 0 ) ? 'NA' : x }

		raw = []
		raw[0] = x_day.unshift( 'x_day' ).join( ',' )
		raw[1] = measured_weight.unshift( l[:data_weight] ).join( ',' )
		raw[2] = bfr.unshift( l[:data_bfr] ).join( ',' )

		puts raw.join( ':' )
		exit

	when 'results'
		html_module = '<div class="row">'
		html_module << "<div class='col-9'><div id='physique_#{mod}-chart' align='center'></div></div>"
		html_module << "<div class='col-3'><div id='physique_#{mod}-chart-sub' align='center'></div>"
		html_module << '</div>'
		html_module << js_chart( mod, l )


	when 'notice'
		puts "CALC energy<br>" if @debug
		r = db.query( "SELECT * FROM #{$TB_KOYOMIEX} WHERE user=? AND date>=?", false, [db.user.name, start_date] )
		r.each do |e|
			unless e['cell'].nil?
				kexc = JSON.parse( e['cell'] )
				recent_weight = kexc['体重'].to_f if kexc['体重'] != nil
			end
		end

		if recent_weight == nil
			puts "こよみ拡張記録に体重データがありません。"
			exit
		end

		m_energy = calc_energy( keep, height, age, sex, pal )
		delta_weight = recent_weight - keep
		delta_energy = 0.0

		if delta_weight > 0
			if delta_weight > 1
				delta_energy = 7200 / 24
				m_energy = (( m_energy - delta_energy ) / 100 ).floor * 100
			else
				delta_energy = delta_weight * 7200 / 24
				m_energy = (( m_energy - delta_energy ) / 100 ).round * 100
			end
		else
			if delta_weight < -1
				delta_energy = -7200 / 24
				m_energy = (( m_energy - delta_energy ) / 100 ).ceil * 100
			else
				delta_energy = delta_weight * 7200 / 24
				m_energy = (( m_energy - delta_energy ) / 100 ).round * 100
			end
		end
		m_energy -= 200 if pgene == 1

		html_module << '<div class="row">'
		html_module << '<div class="col-4">'
		html_module << "<div class='input-group input-group-sm'>"
		html_module << "  <span class='input-group-text'>#{l[:menergy]}</span>"
		html_module << "  <input type='text' class='form-control form-control-sm' id='menergy' value='#{m_energy}' DISABLED>"
		html_module << "</div>"
		html_module << '</div>'

	end


	cfg_kw.set_value( 'pal', pal )
	cfg_kw.set_value( 'keep', keep )
	cfg_kw.set_value( 'start_date', start_date )
	cfg_kw.update

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


def  js_chart( mod, l )
	js = <<-"JS"
<script type='text/javascript'>

var WeightKeepChartDraw = async () => {
	displayBW();

	const startDate = document.getElementById( "start_date" ).value;
	const pal = document.getElementById( "pal" ).value;
	const keep = document.getElementById( "keep" ).value;

	try {
		const response = await fetch( "physique.cgi", {
			method: "POST",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded",
			},
			body: new URLSearchParams({
				mod: "#{mod}",
				step: "raw",
				start_date: startDate,
				pal: pal,
				keep: keep,
			}),
		});

		const raw = await response.text();
		const [xDay, yWeight, yBfr] = raw.split( ":" ).map(( col ) => col.split( "," ));

		if (yWeight.length > 1) {
			const chart = c3.generate({
				bindto: "#physique_#{mod}-chart",

				data: {
					columns: [xDay, yWeight, yBfr],
					x: "x_day",
					axes: {
						#{l[:data_bfr]}: "y2",
					},
					labels: false,
					type: "line",
					colors: {
						#{l[:data_weight]}: "#dc143c",
						#{l[:data_bfr]}: "#228b22",
					},
				},

				axis: {
					x: {
						type: "timeseries",
						tick: {
							culling: true,
							count: 96,
							format: "%m/%d",
						},
					},
					y: {
						type: "linear",
						padding: { top: 100, bottom: 200 },
						tick: { format: d3.format("01d") },
						label: { text: "体重", position: "outer-middle" },
					},
					y2: {
						show: true,
						type: "linear",
						padding: { top: 200, bottom: 100 },
						tick: { format: d3.format("01d") },
						label: { text: "体脂肪率", position: "outer-middle" },
					},
				},

				legend: {
					show: true,
					position: "bottom",
				},
			bar: { width: { ratio: 1.0 }},

				line: { connectNull: true, step: { type: "step" }},
				zoom: { enabled: true, type: "drag" },
				point: { show: true, r: 1 },
			});

//-------------------------------------------------------------------------------
			const daySize = xDay.length - 1;
			const lWeight = ["最新データ"];
			const lBfr = ["l_bfr"];
			const pWeight = ["過去データ"];
			const pBfr = ["p_bfr"];
			const rWeight = ["最近データ"];
			const rBfr = ["r_bfr"];
			const fWeight = ["初回データ"];
			const fBfr = ["f_bfr"];
			let lFlag = true;
			let pFlag = true;


			for ( let i = daySize; i >= 1; i-- ){
				if ( yWeight[i] !== "NA" && yBfr[i] !== "NA" && yWeight[i] != null && yBfr[i] != null ){
					if( lFlag ){
						lWeight.push( yWeight[i] );
						lBfr.push( yBfr[i] );
						lFlag = false;
					}else if( pFlag ) {
						rWeight.push( yWeight[i] );
						rBfr.push( yBfr[i] );
						if( i <= daySize - 23 ){
							pFlag = false;
						}
					}else{
						pWeight.push( yWeight[i] );
						pBfr.push( yBfr[i] );
					}
				}
			}

			if( pWeight.length > 1 ){
				fWeight[1] = pWeight.pop();
				fBfr[1] = pBfr.pop();
			}else if( rWeight.length > 1 ){
				fWeight[1] = rWeight.pop();
				fBfr[1] = rBfr.pop();
			}else{
				fWeight[1] = yWeight[1];
				fBfr[1] = yBfr[1];
			}
			const chartSub = c3.generate({
				bindto: "#physique_#{mod}-chart-sub",

				data: {
					columns: [fWeight, fBfr, pWeight, pBfr, rWeight, rBfr, lWeight, lBfr],
					xs: {
						初回データ: "f_bfr",
						過去データ: "p_bfr",
						最新データ: "l_bfr",
						最近データ: "r_bfr",
					},
					labels: true,
					type: "scatter",
					colors: {
						初回データ: "#4b0082",
						過去データ: "#c0c0c0",
						最近データ: "#00ff00",
						最新データ: "#dc143c",
					},
				},

				axis: {
					x: {
						label: { text: "体脂肪率", position: "outer-center" },
						padding: { left: 1, right: 1 },
						tick: { fit: false, format: d3.format("01d") },
					},
					y: {
						label: { text: "体重", position: "outer-middle" },
						padding: { top: 20, bottom: 20 },
						tick: { fit: false, format: d3.format("01d") },
					},
				},
				grid: {
					x: { show: true },
					y: { show: true },
				},
				legend: { show: true, position: "bottom" },
				point: { show: true, r: 4 },
				tooltip: { show: false },
			});
		} else {
			displayVIDEO( "Non weight data" );
		}
	} catch (error) {
		console.error( "データの取得中にエラーが発生しました:", error );
	}
};


var noticeEER = async () => {
	const startDate = document.getElementById( "start_date" ).value;
	const pal = document.getElementById( "pal" ).value;
	const keep = document.getElementById( "keep" ).value;
	const mod = "#{mod}"

	try {
		const postRes = await fetch( "physique.cgi", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: new URLSearchParams({
				mod: mod, step: "notice", start_date: startDate, pal: pal, keep: keep
			}),
		});
		const data = await postRes.text();

		const element = document.getElementById( "L3" );
		element.innerHTML = data;

		dl3 = true;
		displayBW();

	} catch (error) {
		console.error( "HTMLの取得中にエラーが発生しました:", error );
	}
};

WeightKeepChartDraw();
noticeEER();

</script>
JS
	return js
end


def module_lp( language )
	l = Hash.new
	l['ja'] = {
		mod_name:	"維持チャート",\
		male:		"男性",\
		female:		"女性",\
		chart_name:	"維持チャート",\
		sex:		"代謝的性別",\
		age:		"年齢",\
		height:		"身長（cm）",\
		weight:		"目標維持体重（kg）",\
		start_date:	"開始日",\
		pal:		"身体活動レベル",\
		menergy:	"目安摂取エネルギー（kcal）",\
		data_weight:"体重",\
		data_bfr:	"体脂肪率",\
		label_weight:"体重 (kg)",\
		label_bfr:	"体脂肪率 (%)",\
		data_first:	"開始",\
		data_past:	"過去",\
		data_recent:"近頃",\
		data_latest:	"直近",\
		error_no_set:"設定から生体情報を設定してください。"
	}

	return l[language]
end
