# Config module for sum 0.0.1 (2026/01/02)
#encoding: utf-8

def config_module( cgi, db )
	module_js()
	l = module_lp( db.user.language )
	step = cgi['step']

	if step == 'sum_reset'
		db.query( "UPDATE sum set sum='', name='', code='' WHERE user=?", true, [db.user.name] )
	elsif step == 'meal_reset'
		db.query( "UPDATE meal set meal='', name='', code='' WHERE user=?", true, [db.user.name] )
	end

	html = <<-"HTML"
     <div class="container">
		<div class='row'>
			<div class='col-6'>
				<button type="button" class="btn btn-outline-danger btn-sm nav_button" onclick="sum_cfg( 'sum_reset' )">#{l[:reset_cb]}</button>
			</div>
			<div class='col-6'>
				<button type="button" class="btn btn-outline-danger btn-sm nav_button" onclick="sum_cfg( 'meal_reset' )">#{l[:reset_mt]}</button>
			</div>
		</div>
	</div>
HTML
	return html
end


def module_js()
	js = <<-"JS"
<script type='text/javascript'>

// Chopping board initialisation
var sum_cfg = function( step ){
	postLayer( "config.cgi", '', true, 'L1', { mod:'sum', step });

	flashBW();
	dl1 = true;
	dline = true;
	displayBW();

	if( step == 'sum_reset' ){
		displayVIDEO( 'SUM reset' );

		var fx = function(){ refreshCBN(); };
		setTimeout( fx, 1000 );
	}

	if( step == 'meal_reset' ){
		displayVIDEO( 'MEAL reset' );

		var fx = function(){ refreshMT(); };
		setTimeout( fx, 1000 );
	}
};

</script>
JS
	puts js
end


# Language pack
def module_lp( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		'mod_name'	=> "まな板・お善リセット",
		reset_cb: "まな板をリセット",
		reset_mt: "お善をリセット"
	}

	return l[language]
end
