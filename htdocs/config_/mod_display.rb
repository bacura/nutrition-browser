# Nutorition browser 2020 Config module for NB display 0.04b (2023/7/13)
#encoding: utf-8

@debug = false

def config_module( cgi, db )
	module_js()
	l = module_lp( db.user.language )

	step = cgi['step']

	icache = 0
	ifix = 0
	icalc = 14
	if step ==  'update'
		icache = cgi['icache'].to_i
		ifix = cgi['ifix'].to_i
		icalc = cgi['icalc'].to_i

		# Updating bio information
		db.query( "UPDATE #{$MYSQL_TB_CFG} SET icache='#{icache}', ifix='#{ifix}', icalc='#{icalc}' WHERE user='#{db.user.name}';", true )
	else
		r = db.query( "SELECT * FROM #{$MYSQL_TB_CFG} WHERE user='#{db.user.name}';", false )

		icache = r.first['icache'].to_i
		ifix = r.first['ifix'].to_i
		icalc = r.first['icalc'].to_i
	end

	icalc = 14 if icalc == 0

	html = <<-"HTML"
    <div class="container">
    	<div class='row'>
	    	<div class='col-3'>#{l['cache']}</div>
			<div class='col-4'>
				<div class="custom-control custom-switch">
					<input type="checkbox" class="custom-control-input" id="icache" #{$CHECK[icache == 1]} onchange="display_cfg()">
					<label class="custom-control-label" for="icache"></label>
				</div>
			</div>
		</div>
		<br>
    	<div class='row'>
	    	<div class='col-3'>#{l['fix']}</div>
			<div class='col-4'>
				<div class="custom-control custom-switch">
					<input type="checkbox" class="custom-control-input" id="ifix" #{$CHECK[ifix == 1]} onchange="display_cfg()">
					<label class="custom-control-label" for="ifix">#{l['reload']}</label>
				</div>
			</div>
		</div>
		<br>
    	<div class='row'>
	    	<div class='col-3'>#{l['calc']}</div>
			<div class='col-2'>
				<input class="form-control form-control-sm" type="number" min='5' max='20' id='icalc' value='#{icalc}' onchange="display_cfg()">
			</div>
		</div>
		<br>
 	</div>
HTML
	return html
end


def module_js()
	js = <<-"JS"
<script type='text/javascript'>

// Updating bio information
var display_cfg = function(){
	let icache = 0
	let ifix = 0
	if( document.getElementById( "icache" ).checked ){ icache = 1; }
	if( document.getElementById( "ifix" ).checked ){ ifix = 1; }
	const icalc = document.getElementById( "icalc" ).value;

	$.post( "config.cgi", { mod:'display', step:'update', icache:icache, ifix:ifix, icalc:icalc }, function( data ){
		$( "#L1" ).html( data );
		displayVIDEO( 'Updated' );
	});
};

</script>
JS
	puts js
end


# Language pack
def module_lp( language )
	l = Hash.new

	l['jp'] = {
		'mod_name' => "表示",\
		'cache' => "画像キャッシュ",\
		'fix' => "メニューの固定:",\
		'reload' => "※更新後、リロードが必要です",\
		'calc' => "1行の栄養素表示数"
	}

	return l[language]
end
