# Ginmi module for METs 0.10b (2024/04/11)
#encoding: utf-8

@debug = false

def ginmi_module( cgi, db )
	l = module_lp( db.user.language )
	module_js( cgi['mod'] )

	command = cgi['command']
	weight = cgi['weight']
	heading = cgi['heading']
	sub_heading = cgi['sub_heading']
	active = cgi['active']
	history = cgi['history']
	hh = cgi['hh'].to_i
	mm = cgi['mm'].to_i
	mets = cgi['mets'].to_s
	denergy = cgi['denergy'].to_s
	yyyy_mm_dd = cgi['yyyy_mm_dd']
	active = history if history != '0' &&  history != ''

	html = ''
	case command
	when 'form'
		puts "Load bio config" if @debug
		weight = 0.0
		kexow = 0
		r = db.query( "SELECT bio FROM #{$MYSQL_TB_CFG} WHERE user='#{db.user.name}';", false )
		if r.first
			if r.first['bio'] != nil && r.first['bio'] != ''
				bio = JSON.parse( r.first['bio'] )
				weight = bio['weight'].to_f
				kexow = bio['kexow'].to_i
			end
		end

		puts "IMPORT height & weight from KEX" if @debug
		if kexow == 1
			weight_flag = true
			r = db.query( "SELECT cell FROM #{$MYSQL_TB_KOYOMIEX} WHERE user='#{db.user.name}' AND cell !='' AND cell IS NOT NULL ORDER BY date DESC;", false )
			r.each do |e|
				kexc = JSON.parse( e['cell'] )
				if weight_flag && e['体重'] != nil
					weight = kexc['体重'].to_f
					weight_flag = false
				end

				break unless weight_flag
			end
		end

	when 'result', 'display'
		mets_mm = hh * 60 + mm
		mets = ''
		r = db.query( "SELECT * FROM #{$MYSQL_TB_METS} WHERE user='#{db.user.name}' and name='default';", false )
		if r.first
			mets = r.first['mets']
			if command == 'result'
				mets = "#{mets}\t#{active}:#{mets_mm}"
				db.query( "UPDATE #{$MYSQL_TB_METS} SET mets='#{mets}' WHERE user='#{db.user.name}' and name='default';", true )
			end
		elsif command == 'result'
			db.query( "INSERT INTO #{$MYSQL_TB_METS} SET user='#{db.user.name}', name='default',mets='#{active}:#{mets_mm}';", true )
			mets << "#{active}:#{mets_mm}"
		end

		code_set = []
		mm_set = []
		total_mm = 0.0
		total_hm = ''
		total_energy = 0
		total_d_energy = 0
		total_mets = BigDecimal( 0 )
		total_d_mets = BigDecimal( 0 )
		a = mets.split( "\t" )
		a.size.times do |c|
			aa = a[c].split( ':' )
			code_set << aa[0]
			mm_set << aa[1].to_i
		end

		mets_table_html = '<table class="table table-hover table-sm">'
		mets_table_html << '<thead>'
		mets_table_html << '<tr class="">'
		mets_table_html << '<td>Code</td>'
		mets_table_html << '<td>個別活動</td>'
		mets_table_html << '<td>METs</td>'
		mets_table_html << '<td>時間(h)</td>'
		mets_table_html << '<td>METs*h</td>'
		mets_table_html << '<td>時間 [累積]</td>'
		mets_table_html << '</tr>'
		mets_table_html << '</thead>'

		code_set.size.times do |c|
			r = db.query( "SELECT * FROM #{$MYSQL_TB_METST} WHERE code='#{code_set[c]}';", false )
			if r.first
				mets = BigDecimal( r.first['mets'] )
				d_mets = BigDecimal( r.first['mets'] ) - 1

				hh_ = sprintf( "%.3f", ( mm_set[c].to_f / 60 ).round( 3 ).to_s )
				metsh = mets * mm_set[c].to_f / 60
				d_metsh = d_mets * mm_set[c].to_f / 60

				metsh_ = sprintf( "%.3f", metsh.round( 3 ).to_s )
				d_metsh_ = sprintf( "%.3f", d_metsh.round( 3 ).to_s )

				total_mets += metsh
				total_d_mets += d_metsh
				total_energy += ( metsh * weight.to_f * 1.05 )
				total_d_energy += ( d_metsh * weight.to_f * 1.05 )
				total_mm += mm_set[c]

				h = mm_set[c].div( 60 )
				m = mm_set[c] % 60
				if m < 10
					m = "0#{m.to_i}"
				else
					m = m.to_i
				end
				hm = "#{h}:#{m}"

				th = total_mm.div( 60 )
				tm = total_mm % 60
				if tm < 10
					tm = "0#{tm.to_i}"
				else
					tm = tm.to_i
				end
				total_hm = "#{th}:#{tm}"

				mets_table_html << '<tr>'
				mets_table_html << "<td>#{r.first['code']}</td><td>#{r.first['active']}</td><td>#{mets.to_f}</td><td>#{hh_}</td><td>#{metsh_}</td><td>#{hm} [#{total_hm}]</td>"
				mets_table_html << '</tr>'
			end
		end
		mets_table_html << '</table>'

		result_html = <<-"RESULT_HTML"
		<div class='row'>
			<div class='col-2'>合計METs*h</div>
			<div class='col-8'>#{total_mets.to_f.round( 3 )}</div>
			<div class='col-2'>
				<button class='btn btn-sm btn-outline-danger' onclick="ginmiEnergyMETsreset()">リセット</button>
			</div>
		</div>
		<div class='row'>
			<div class='col-2'>消費エネルギー</div>
			<div class='col-2'>#{total_energy.to_i} kcal</div>
			<div class='col-1'>計算式</div>
			<div class='col-5'>#{weight} * #{total_mets.to_f.round( 3 )} * 1.05</div>
		</div>
		<div class='row'>
			<div class='col-2'>Δ消費エネルギー</div>
			<div class='col-2'>#{total_d_energy.to_i} kcal</div>
			<div class='col-1'>計算式</div>
			<div class='col-5'>#{weight} * ( #{total_mets.to_f.round( 3 )} - #{(total_mm.to_f / 60 ).round( 3 )} ) * 1.05</div>
		</div>
RESULT_HTML

		puts result_html
		puts mets_table_html

		calendar = Calendar.new( user.name, 0, 0, 0 )
		puts "<div class='row'>"
		puts "	<div class='col-8'></div>"
		puts "	<div class='col-4' align='right'>"
		puts "		<div class='input-group'>"
		puts "			<input type='date' class='form-control form-control-sm' id='yyyy_mm_dd' value='#{calendar.yyyy}-#{calendar.mms}-#{calendar.dd}'>"
		puts "			<button class='btn btn-sm btn-outline-success' onclick=\"ginmiKEXout( '#{total_mets.to_f.round( 3 )}', '#{total_d_energy.to_i}' )\">＋拡張こよみ</button>"
		puts "		</div>"
		puts "	</div>"
		puts "</div>"


		if command == 'result'
			r = db.query( "SELECT * FROM #{$MYSQL_TB_METS} WHERE user='#{db.user.name}' AND name='history';", false )
			if r.first
				a = r.first['mets'].split( "\t" )
				a.unshift( active ).uniq!
				limit = 19
				limit = a.size - 1 if a.size < 19
				if a.size == 1
					new_history = active
				else
					new_history = a[0..limit].join( "\t" )
				end
				db.query( "UPDATE #{$MYSQL_TB_METS} SET mets='#{new_history}' WHERE user='#{db.user.name}' AND name='history';", true )
			else
				db.query( "INSERT INTO #{$MYSQL_TB_METS} SET user='#{db.user.name}', name='history', mets='#{active}';", true )
			end
		end
		exit( 0 )

	when 'reset'
		db.query( "delete from #{$MYSQL_TB_METS} WHERE user='#{db.user.name}' and name='default';", true )
		exit( 0 )

	when 'kexout'
		r = db.query( "SELECT koyomi FROM #{$MYSQL_TB_CFG} WHERE user='#{db.user.name}';", false )
		if r.first
			if r.first['koyomi'] != nil && r.first['koyomi'] != ''
				koyomi = JSON.parse( r.first['koyomi'] )
				kex_unit = koyomi['kexu']
				kex_active = koyomi['kexa']
			end
		end

		r = db.query( "SELECT * FROM #{$MYSQL_TB_KOYOMIEX} WHERE user='#{db.user.name}' AND date='#{yyyy_mm_dd}';", false )
		db.query( "INSERT INTO #{$MYSQL_TB_KOYOMIEX} SET user='#{db.user.name}', date='#{yyyy_mm_dd}';", true ) unless r.first

		cell = Hash.new
		cell = JSON.parse( r.first['cell'] ) if r.first['cell'] != nil
		cell[l['mets']] = mets if kex_active[l['mets']] == '1'
		cell[l['denergy']] = denergy if kex_active[l['denergy']] == '1'

		cell_ = JSON.generate( cell )
		db.query( "UPDATE #{$MYSQL_TB_KOYOMIEX} SET cell='#{cell_}' WHERE user='#{db.user.name}' AND date='#{yyyy_mm_dd}';", true )
		exit( 0 )
	end


	####
	heading_select = ''
	r = db.query( "SELECT DISTINCT heading FROM #{$MYSQL_TB_METST};", false )
	heading = r.first['heading'] if heading == ''
	r.each do |e|
		if e['heading'] == heading
			heading_select << "<option value='#{e['heading']}' SELECTED>#{e['heading']}</option>"
		else
			heading_select << "<option value='#{e['heading']}'>#{e['heading']}</option>"
		end
	end

	####
	sub_heading_select = ''
	r = db.query( "SELECT DISTINCT sub_heading FROM #{$MYSQL_TB_METST} WHERE heading='#{heading}';", false )
	sub_heading = r.first['sub_heading'] if sub_heading == ''
	r.each do |e|
		if e['sub_heading'] == sub_heading
			sub_heading_select << "<option value='#{e['sub_heading']}' SELECTED>#{e['sub_heading']}</option>"
		else
			sub_heading_select << "<option value='#{e['sub_heading']}'>#{e['sub_heading']}</option>"
		end
	end

	####
	active_select = ''
	mets_value = '0.0'
	r = db.query( "SELECT * FROM #{$MYSQL_TB_METST} WHERE sub_heading='#{sub_heading}';", false )
	mets_value = r.first['mets']
	r.each do |e|
		if e['code'] == active
			active_select << "<option value='#{e['code']}' SELECTED>#{e['active']}</option>"
			mets_value = e['mets']
		else
			active_select << "<option value='#{e['code']}'>#{e['active']}</option>"
		end
	end


	####
	history_select = "<option value='0'>↓↓</option>"
	r = db.query( "SELECT mets FROM #{$MYSQL_TB_METS} WHERE user='#{db.user.name}' AND name='history';", false )
	if r.first
		a = r.first['mets'].split( "\t" )
		a.each do |e|
			rr = db.query( "SELECT * FROM #{$MYSQL_TB_METST} WHERE code='#{e}';", false )
			history_select << "<option value='#{e}'>[#{e}] #{rr.first['active']}</option>"
		end
	end


	r = db.query( "SELECT koyomi FROM #{$MYSQL_TB_CFG} WHERE user='#{db.user.name}';", false )
	if r.first
		if r.first['koyomi'] != nil && r.first['koyomi'] != ''
			koyomi = JSON.parse( r.first['koyomi'] )
			start = koyomi['start'].to_i
			kex_select = koyomi['kex_select']
		end
	end


	html = <<-"HTML"
	<div class='row'>
	<h5>METs 計算フォーム</h5>
	</div>
	<br>

	<div class='row'>
		<div class='col-4'>
			<div class='input-group input-group-sm'>
				<span class='input-group-text'>体重(kg)</span>
				<input type='text' class='form-control' id='weight' maxlength='6' value='#{weight}'>
			</div>
		</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-6'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="heading">　大項目</label>
				<select class="form-select form-select-sm" id="heading" onchange="ginmiEnergyMETs( 'heading' )">
					#{heading_select}
				</select>
			</div>
		</div>
		<div class='col-6'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="inputGroupSelect01">履　　歴</label>
				<select class="form-select form-select-sm" id="history">
					#{history_select}
				</select>
			</div>
		</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-6'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="sub_heading">　副項目</label>
				<select class="form-select form-select-sm" id="sub_heading" onchange="ginmiEnergyMETs( 'sub_heading' )">
					#{sub_heading_select}
				</select>
			</div>
		</div>
		<div class='col-2'>
			<div class='input-group input-group-sm'>
				<input type='number' class='form-control' value="#{mets_value}" DISABLED>
				<span class='input-group-text'>METs</span>
			</div>
		</div>
		<div class='col-2'>
			<div class='input-group input-group-sm'>
				<input type='number' min='0' max='24' class='form-control' id='hh' maxlength='2' value='0'>
				<span class='input-group-text'>時間</span>
			</div>
		</div>
		<div class='col-2'>
			<div class='input-group input-group-sm'>
				<input type='number' min='0' max='59' step='5' class='form-control' id='mm' maxlength='2' value='0'>
				<span class='input-group-text'>分間</span>
			</div>
		</div>
	</div>
	<br>

	<div class='row'>
		<div class='col-6'>
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="active">個別活動</label>
				<select class="form-select form-select-sm" id="active" onchange="ginmiEnergyMETs( 'active' )">
					#{active_select}
				</select>
			</div>
		</div>
	</div>
	<br>
	<div class='row'>
		<button class='btn btn-sm btn-info' onclick="ginmiEnergyMETsres()">#{l['add']}</button>
	</div>
HTML

	return html
end


def module_js( mod )
	js = <<-"JS"
<script type='text/javascript'>

var ginmiEnergyMETskex = function(){
	$.post( "ginmi.cgi", { mod:'#{mod}', command:'koyomiex' }, function( data ){ $( "#L1" ).html( data );});

	flashBW();
	dl1 = true;
	dline = true;
	displayBW();
};

var ginmiEnergyMETs = function( select ){
	const weight = document.getElementById( "weight" ).value;
	const heading = document.getElementById( "heading" ).value;
	let sub_heading = '';
	let active = '';

	if( select == 'sub_heading'){
		sub_heading = document.getElementById( "sub_heading" ).value;
		$.post( "ginmi.cgi", { mod:'#{mod}', command:'', weight:weight, heading:heading, sub_heading:sub_heading }, function( data ){ $( "#L1" ).html( data );});
	} else if( select == 'active'){
		sub_heading = document.getElementById( "sub_heading" ).value;
		active = document.getElementById( "active" ).value;
		displayVIDEO( active );
		$.post( "ginmi.cgi", { mod:'#{mod}', command:'', weight:weight, heading:heading, sub_heading:sub_heading, active:active }, function( data ){ $( "#L1" ).html( data );});
	} else{
		$.post( "ginmi.cgi", { mod:'#{mod}', command:'', weight:weight, heading:heading }, function( data ){ $( "#L1" ).html( data );});
	}
};

var ginmiEnergyMETsres = function(){
	const weight = document.getElementById( "weight" ).value;
	const active = document.getElementById( "active" ).value;
	const hh = document.getElementById( "hh" ).value;
	const mm = document.getElementById( "mm" ).value;
	const history = document.getElementById( "history" ).value;

	if( weight != '' && weight != '0'){
		if( hh == '0' && mm == '0'){
			displayVIDEO( 'Time! (>_<)' );
			$.post( "ginmi.cgi", { mod:'#{mod}', command:'display', weight:weight, active:active, history:history, hh:hh, mm:mm }, function( data ){ $( "#L2" ).html( data );});
		}else{
			$.post( "ginmi.cgi", { mod:'#{mod}', command:'result', weight:weight, active:active, history:history, hh:hh, mm:mm }, function( data ){ $( "#L2" ).html( data );});
			setTimeout( ginmiEnergyMETs( 'active' ), 1000 );
		}
	}else{
		displayVIDEO( 'Weight! (>_<)' );
	}

	dl2 = true;
	displayBW();
};

var ginmiEnergyMETsreset = function(){
	displayVIDEO( 'METs reset' );
	$.post( "ginmi.cgi", { mod:'#{mod}', command:'reset' }, function( data ){ $( "#L2" ).html( data );});
	dl2 = false;
	displayBW();
};

var ginmiKEXout = function( mets, denergy ){
	const yyyy_mm_dd = document.getElementById( 'yyyy_mm_dd' ).value;
	$.post( "ginmi.cgi", { mod:'#{mod}', command:'kexout', mets:mets, denergy:denergy, yyyy_mm_dd:yyyy_mm_dd}, function( data ){
//		$( "#L3" ).html( data );
//		dl3 = true;
//		displayBW();

		displayVIDEO( 'KoyomiEX' );
	});
};

</script>
JS
	puts js
end

def module_lp( language )
	l = Hash.new
	l['jp'] = {
		'mod_name' => "METs計算",\
		'title' => "BMI 計算フォーム",\
		'age' => "年齢",\
		'height' => "身長(m)",\
		'weight' => "体重(kg)",\
		'calc' => "計算",\
		'add' => "追加 / 表示",\
		'mets' => "METs",\
		'denergy' => "Δエネルギー"
	}

	return l[language]
end
