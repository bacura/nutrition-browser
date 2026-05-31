# Nutorition browser 2020 Config module for Fitbit 0.0.0 (2026/05/12)
#encoding: utf-8

@debug = false

def config_module( cgi, db )
	module_js( cgi['mod'] )
	l = module_lp( db.user.language )
	step = cgi['step']

	res = db.query( "SELECT fitbit FROM #{$TB_CFG} WHERE user=?", false, [db.user.name] )&.first
	unless res['fitbit'].to_s.empty?
		begin
			fitbit = JSON.parse( res['fitbit'] )
		rescue JSON::ParserError => e
			puts "J(x_x)pE: #{e.message}<br>"
			exit
		end     

		client_id = fitbit['client_id'].to_s
		client_secret = fitbit['client_secret'].to_s
	end

	if step ==  'change'
		client_id = cgi['client_id'].to_s
		client_secret = cgi['client_secret'].to_s

		# Updating bio information
		fitbit_ = JSON.generate({ "client_id" => client_id, "client_secret" => client_secret })
		db.query( "UPDATE #{$TB_CFG} SET fitbit=? WHERE user=?", true, [fitbit_, db.user.name] )
	end

	auth_button = ''
	if client_id && db.user.status >= 8
		scopes   = 'activity weight'
		auth_url = "https://www.fitbit.com/oauth2/authorize?" \
			"response_type=code" \
			"&client_id=#{client_id}" \
			"&redirect_uri=#{URI.encode_www_form_component( $FITBIT_REDIRECT_URI )}" \
			"&scope=#{URI.encode_www_form_component( scopes )}" \
			"&state=fitbit"

		auth_button = "<button class='btn btn-warning btn-sm' type='button' onclick=\"window.open( '#{auth_url}', 'fitbit' );\">#{l[:auth2]}</button>"
	end

	html = <<~"HTML"
    <div class="container">
    	<div class='row'>
	    	<div class='row'>
		    	<div class='col-2'>#{l[:auth_id]}</div>
				<div class='col-4'><input type="text" id="client_id" class="form-control login_input" value="#{client_id}"></div>
			</div>

	    	<div class='row'>
		    	<div class='col-2'>#{l[:secret]}</div>
				<div class='col-4'><input type="text" id="client_secret" class="form-control login_input" value="#{client_secret}"></div>
			</div>
		</div>
		<hr>

    	<div class='row'>
			<div class='col-2'><button type="button" class="btn btn-outline-primary btn-sm nav_button" onclick="fitbit_cfg( 'change' )">#{l[:save]}</button></div>
			<div class='col-2'>#{auth_button}</div>
		</div>
	</div>
HTML
	return html
end


def module_js( mod )
	js = <<-"JS"
<script type='text/javascript'>

// Updating bio information
var fitbit_cfg = function( step ){
	let client_id = '';
	let client_secret = '';

	if( step == 'change' ){
		client_id = document.getElementById( "client_id" ).value;
		client_secret = document.getElementById( "client_secret" ).value;
	}
	postLayer( 'config.cgi', 'dummy', true, 'L1', { mod:'#{mod}', step, client_id, client_secret });

	flashBW();
	dl1 = true;
	dline = true;
	displayBW();
};


</script>
JS
	puts js
end


def module_lp( language )
	l = Hash.new
	l['ja'] = {
		'mod_name' => "Fitbit(テスト)",
		auth_id: "OAuth 2.0 Client ID",
		secret: "Client Secret",
		save: "保存",
		auth2: "認証"
	}

	return l[language]
end
