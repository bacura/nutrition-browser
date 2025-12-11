# Nutorition browser 2020 Config module for koyomiex 0.3.0 (2025/08/21)
#encoding: utf-8

@debug = false
@kex_max = 10

def config_module( cgi, db )
	module_js()
	l = module_lp( db.user.language )

	koyomi = Hash.new
	start = "#{Time.new.year}-01-01"
	kexu = Hash.new
	kexa = Hash.new
	kexg = Hash.new
	kexup = Hash.new
	kexbtm = Hash.new

	html = []

	step = cgi['step']
	kex_key = cgi['kex_key']
	kex_add_key = cgi['kex_add_key']
	kex_add_unit = cgi['kex_add_unit']
	kex_add_select = cgi['kex_add_select']
	kex_goal = cgi['kex_goal']
	kex_upper = cgi['kex_upper']
	kex_bottom = cgi['kex_bottom']
	preset_select = cgi['preset_select'].to_s
	if @debug
		puts "step: #{step}<br>"
		puts "preset_select: #{preset_select}<br>"
	end


	puts 'LOAD config<br>' if @debug
	res = db.query( "SELECT koyomi FROM #{$MYSQL_TB_CFG} WHERE user=?", false, [db.user.name] )&.first
	if res
		if res['koyomi'].to_s != ''
			begin
				koyomi = JSON.parse( res['koyomi'] )
    		rescue JSON::ParserError => e
      			puts "JSON parse error: #{e.message}<br>" if @debug
    		end			
			start = koyomi['start'] unless koyomi['start'].nil?
			kexu = koyomi['kexu'] unless koyomi['kexu'].nil?
			kexa = koyomi['kexa'] unless koyomi['kexa'].nil?
			kexg = koyomi['kexg'] unless koyomi['kexg'].nil?
			kexup = koyomi['kexup'] unless koyomi['kexup'].nil?
			kexbtm = koyomi['kexbtm'] unless koyomi['kexbtm'].nil?
		end
	end


	case step
	when 'kstart'
		start = cgi['kstart'].to_s
		puts "start: #{start}<br>" if @debug

	when 'new'
		kexu[kex_add_key] = kex_add_unit
		kexa[kex_add_key] = "1"

	when 'select'
		kexu[kex_add_select] = @kex_std[kex_add_select]
		kexa[kex_add_select] = "1"

	when 'delete'
		kexu.delete( kex_key )
		kexa.delete( kex_key )

	when 'available'
		kex_onoff = cgi['kex_onoff']
		kexa[kex_key] = kex_onoff

	when 'change_value'
		kexg[kex_key] = cgi['kex_goal'] == '' ? '' : cgi['kex_goal'].to_f
		kexup[kex_key] = cgi['kex_upper'] == '' ? '' : cgi['kex_upper'].to_f
		kexbtm[kex_key] = cgi['kex_bottom'] == '' ? '' : cgi['kex_bottom'].to_f

	when 'preset_apply'
 		koyomi_ = @kex_presets[preset_select]

		begin
			koyomi = JSON.parse( koyomi_ )
		rescue JSON::ParserError => e
  			puts "JSON parse error: #{e.message}<br>" if @debug
		end

		kexu = koyomi['kexu'] unless koyomi['kexu'].nil?
		kexa = koyomi['kexa'] unless koyomi['kexa'].nil?
		kexg = koyomi['kexg'] unless koyomi['kexg'].nil?
		kexup = koyomi['kexup'] unless koyomi['kexup'].nil?
		kexbtm = koyomi['kexbtm'] unless koyomi['kexbtm'].nil?
	end


	puts 'UPDATE config<br>' if @debug
	if step != ''
		koyomi['start'] = start
		koyomi['kexu'] = kexu
		koyomi['kexa'] = kexa
		koyomi['kexg'] = kexg
		koyomi['kexup'] = kexup
		koyomi['kexbtm'] = kexbtm
		koyomi_ = JSON.generate( koyomi )

		db.query( "UPDATE #{$MYSQL_TB_CFG} SET koyomi=? WHERE user=?", true, [koyomi_, db.user.name] )
	end


	puts 'HTML start year <br>' if @debug
	koyomi_start = "<input type='date' class='form-control' id='kstart' value='#{start}' onchange='ksChange()'>"


	puts 'Options from KEX Preset<br>' if @debug
	preset_opt = '<option value="">-</option>'
	@kex_presets.each do |k, v|
		begin
			kex_preset =  JSON.parse( v )
			preset_opt << "<option value='#{k}'>#{kex_preset['name']}</option>"
    	rescue JSON::ParserError => e
      		puts "JSON parse error: #{e.message}<br>" if @debug
    	end			
	end


	puts 'HTML10<br>' if @debug
	html[10] = <<~HTML10
	<div class="container">
		<div class='row'>
			<div class='col-3'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>#{l[:start]}</span>
					#{koyomi_start}
				</div>
			</div>
		</div>
		<hr>

		<div class='row'>
			<div class='col-6'>
				<h5>#{l[:menu_title]}</h5>
			</div>
			<div class='col-6'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>#{l[:preset]}</span>
					<select class='form-select' id='preset_select'>
						#{preset_opt}
					</select>
					<button type='button' class='btn btn-warning btn-sm' onclick='applyPreset()'>#{l[:apply]}</button>
				</div>
			</div>
		</div>
		<br>
	HTML10


	puts 'HTML20<br>' if @debug
	html[20] = ''
	kexu.each do |k, v|
		ht = <<~HT
		<div class='row'>
			<div class='col-1'>
				<div class='form-check form-switch'>
					<input class='form-check-input' type='checkbox' id='kex_onoff#{k}' #{$CHECK[kexa[k] == '1']} onchange=\"kexOnOff( '#{k}' )\">
				</div>
			</div>
			<div class='col-4'>
				<div class='input-group input-group-sm'>
    				<label class='input-group-text'>#{l[:item]}</label>
					<input type='text' maxlength='64' id='kex_key#{k}' class='form-control form-control-sm' value='#{k}' DISABLED>
				</div>
			</div>
			<div class='col-2'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>#{l[:unit]}</span>
					<input type='text' maxlength='32' id='kex_unit#{k}' class='form-control form-control-sm' value='#{v}' DISABLED>
				</div>
			</div>
			<div class='col-1'>
				<input type='text' maxlength='6' id='kex_goal#{k}' class='form-control form-control-sm' value='#{kexg[k]}' placeholder='#{l[:goal]}' onchange=\"kexChangeValue( '#{k}' )\">
			</div>
			<div class='col-1'>
				<input type='text' maxlength='6' id='kex_upper#{k}' class='form-control form-control-sm' value='#{kexup[k]}' placeholder='#{l[:upper]}' onchange=\"kexChangeValue( '#{k}' )\">
			</div>
			<div class='col-1'>
				<input type='text' maxlength='6' id='kex_bottom#{k}' class='form-control form-control-sm' value='#{kexbtm[k]}' placeholder='#{l[:bottom]}' onchange=\"kexChangeValue( '#{k}' )\">
			</div>
			<div class='col-1'></div>
			<div class='col'><input type='checkbox' id='kex_del#{k}'>&nbsp;<span onclick=\"kexDel( '#{k}' )\">#{l[:init]}</span></div>
		</div><br>
		HT

		html[20] << ht
	end

	if kexu.size <= @kex_max
		option = ''
		@kex_std.each do |k, v|
			option << "<option value='#{k}'>#{k} (#{v})</option>" unless kexu.key?( k )
		end

		puts 'HTML30<br>' if @debug
		html[30] = <<~HTML30
		<hr>
		<div class='row'>
			<div class='col-1'></div>
			<div class='col-4'>
				<div class='input-group input-group-sm'>
					<label class='input-group-text'>#{l[:koho]}</label>
					<select class='form-select' id='kex_add_select'>
						#{option}
					</select>
				</div>
			</div>
			<div class='col'><button type='button' class='btn btn-dark btn-sm' onclick="kexAdd()">#{l[:add]}</button></div>
		</div><br>

		<div class='row'>
			<div class='col-1'></div>
			<div class='col-4'>
				<div class='input-group input-group-sm'>
					<label class='input-group-text'>#{l[:novel]}</label>
					<input type='text' maxlength='32' id='kex_add_key' class='form-control form-control-sm' value=''>
				</div>
			</div>
			<div class='col-2'>
				<div class='input-group input-group-sm'>
					<span class='input-group-text'>#{l[:unit]}</span>
					<input type='text' maxlength='32' id='kex_add_unit' class='form-control form-control-sm' value=''>
				</div>
			</div>
			<div class='col-4'></div>
			<div class='col'><button type='button' class='btn btn-dark btn-sm' onclick="kexNew()">#{l[:add]}</button></div>
		</div><br>
		HTML30
	end

	return html.join
end


def module_js()
	js = <<-"JS"
<script type='text/javascript'>

var ksChange = () => {
	const kstart = document.getElementById( 'kstart' ).value;
    postLayer( 'config.cgi', '', true, 'L1', { mod:'koyomi', step:'kstart', kstart });
};

var kexAdd = () => {
	const kex_add_select = document.getElementById( 'kex_add_select' ).value;
    postLayer( 'config.cgi', '', true, 'L1', { mod:'koyomi', step:'select', kex_add_select });
};

var kexNew = () => {
	const kex_add_key = document.getElementById( 'kex_add_key' ).value;
	const kex_add_unit = document.getElementById( 'kex_add_unit' ).value;

	if( kex_add_key != '' ){
		postLayer( 'config.cgi', '', true, 'L1', { mod:'koyomi', step:'new', kex_add_key, kex_add_unit });
	}
};

var kexOnOff = ( kex_key ) => {
	const kex_onoff = document.getElementById( 'kex_onoff' + kex_key )?.checked ? 1 : 0;
	postLayer( 'config.cgi', '', true, 'L1', { mod:'koyomi', step:'available', kex_key, kex_onoff });
};

var kexDel = ( kex_key ) => {
	const checkbox = document.getElementById( 'kex_del' + kex_key );
	if ( checkbox?.checked ) {
		postLayer( 'config.cgi', '', true, 'L1', { mod:'koyomi', step:'delete', kex_key });
	}else{
		displayVIDEO( "Check!(>_<)" );
	}
};

var kexChangeValue = ( kex_key ) => {
	const kex_goal = document.getElementById( 'kex_goal' + kex_key ).value;
	const kex_upper = document.getElementById( 'kex_upper' + kex_key ).value;
	const kex_bottom = document.getElementById( 'kex_bottom' + kex_key ).value;
	postLayer( 'config.cgi', '', true, 'L1', { mod:'koyomi', step:'change_value', kex_key, kex_goal, kex_upper, kex_bottom });
};

var applyPreset = () => {
	const preset_select = document.getElementById( 'preset_select' ).value;
	if( preset_select != '' ){
		postLayer( 'config.cgi', '', true, 'L1', { mod:'koyomi', step:'preset_apply', preset_select });
	}
};


</script>
JS
	puts js
end


def module_lp( language )
	l = Hash.new
	l['jp'] = {
		'mod_name'	=> "こよみ",
		mod_name: "こよみ",
		start: "こよみ開始日",
		menu_title: "こよみ拡張:",
		item: "項目名",
		org_name: "名称",
		unit: "単位",
		add: "＋",
		koho: "候　補",
		novel: "新　規",
		goal: "目標値",
		upper: "上限値",
		bottom: "下限値",
		preset: "プリセット",
		apply: "適用",
		init: "<img src='bootstrap-dist/icons/trash.svg' style='height:1.8em; width:1.8em;'>"
	}

	return l[language]
end
