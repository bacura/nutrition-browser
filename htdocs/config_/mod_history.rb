# Nutorition browser 2020 Config module for history 0.03b (2023/7/13)
#encoding: utf-8

def config_module( cgi, db )
	module_js()
	l = module_lp( db.user.language )
	history = Hash.new
	his_max = 200

	puts "LOAD config<br>" if @debug
	r = db.query( "SELECT history FROM #{$MYSQL_TB_CFG} WHERE user='#{db.user.name}';", false )
	if r.first
		if r.first['history'] != nil && r.first['history'] != ''
			history = JSON.parse( r.first['history'] )
			his_max = history['his_max'].to_i if history['his_max']
		end
	end

	case cgi['step']
	when 'max'
		puts "UPDATE max<br>" if @debug
		his_max = cgi['his_max'].to_i
		his_max = 200 if his_max == nil || his_max == 0 || his_max > 1000

		history['his_max'] = his_max
		history_ = JSON.generate( history )
		db.query( "UPDATE #{$MYSQL_TB_CFG} SET history='#{history_}' WHERE user='#{db.user.name}';", true )

	when 'clear'
		puts "CLEAR history<br>" if @debug
		db.query( "UPDATE #{$MYSQL_TB_HIS} SET his='' WHERE user='#{db.user.name}';", true )
	end

	html = <<-"HTML"
     <div class="container">

      	<div class='row'>
      		<h5>#{l['his_vol']}</h5>
      	</div>
     	<div class='row'>
			<div class='col-2'>#{his_max} #{l['food']}</div>
			<div class='col-1' align='right'>200</div>
			<div class='col-3'>
				<input type="range" class="custom-range" min="200" max="1000" step="100" value='#{his_max}' id="his_max" onchange="history_cfg( 'max' )">
			</div>
			<div class='col-1'>1000</div>
		</div>
		<br>
     	#{l['msg1']}

     	<hr>
      	<div class='row'>
    		#{l['msg2']}<br>
    	</div>
    	<br>
		<button type="button" class="btn btn-outline-danger btn-sm nav_button" onclick="history_cfg( 'clear' )">#{l['init']}</button>
	</div>
HTML
	return html
end


def module_js()
	js = <<-"JS"
<script type='text/javascript'>

// History initialisation
var history_cfg = function( step ){
	const his_max = document.getElementById( "his_max" ).value;
	$.post( "config.cgi", { mod:'history', step:step, his_max:his_max }, function( data ){
			$( "#L1" ).html( data );

			flashBW();
			dl1 = true;
			dline = true;
			displayBW();
	});

	if( step == 'clear' ){
		displayVIDEO( 'Initialized' );
	}
	if( step == 'max' ){
		displayVIDEO( 'History max -> '+ his_max );
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
	l['jp'] = {
		'mod_name'	=> "履歴",\
		'his_vol'	=> "履歴保存量",\
		'msg1'	=> "※増やすとレスポンスが悪くなるかもしれません。",\
		'msg2'	=> "履歴を初期化する場合は、履歴初期化ボタンを押してください。",\
		'init' 	=> "履歴初期化",\
		'food'	=> "食品"
	}

	return l[language]
end
