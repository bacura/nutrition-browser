# Nutorition browser 2020 Config module for release 0.0.3.AI (24/08/20)
#encoding: utf-8

# Debug mode
@debug = false

def config_module( cgi, db )
	render_javascript()
	l = module_lp( db.user.language )

	step = cgi['step']
	password = cgi['password']
	debug_output( step, password )

	if step.empty?
		debug_output( 'form step' )
		html = render_form( l )
	else
		if db.user.status != 3 && db.user.status != 9
			debug_output( 'release step general' )
			html = render_general_release( l )
			update_user_status( db )
			delete_user_data( db )

		else
			debug_output( 'release step ROM' )
			html = render_rom_release( l )
		end
	end

	return html
end

def render_form( l )
	<<-"HTML"
		<div class="container">
			<div class='row'>
				#{l['msg']}<br>
			</div><br>
			<div class='row'>
				<div class='col-4'><input type="password" id="password" class="form-control form-control-sm login_input" placeholder="#{l['password']}" required></div>
				<div class='col-4'><button type="button" class="btn btn-outline-danger btn-sm nav_button" onclick="release_cfg()">#{l['release']}</button></div>
			</div>
		</div>
	HTML
end

def render_general_release( l )
	<<-"HTML"
		<div class="container">
			<div class='row'>
				#{l['thanks']}
			</div>
		</div>
	HTML
end

def update_user_status( db )
	db.query( "UPDATE #{$MYSQL_TB_USER} SET status='0' WHERE user='#{db.user.name}' AND cookie='#{db.user.uid}';", true )
end

def delete_user_data( db )
	[
		$MYSQL_TB_HIS, 
		$MYSQL_TB_SUM, 
		$MYSQL_TB_CFG, 
		$MYSQL_TB_MEAL,
		$MYSQL_TB_PRICEM, 
		$MYSQL_TB_PALETTE
	].each do |table|
		db.query( "DELETE FROM #{table} WHERE user='#{db.user.name}';", true )
	end
end

def render_rom_release( l )
	<<-"HTML"
		<div class="container">
			<div class='row'>
				#{l['nguser']}
			</div>
		</div>
	HTML
end

def render_javascript()
	js = <<-"JS"
<script type='text/javascript'>
	var release_cfg = function(){
		const password = $( "#password" ).val();

		$.post( "config.cgi", { mod:'release', step:'release', password:password }, function( data ){
			$( "#L1" ).html( data );
			flashBW();
			dl1 = true;
			dline = true;
			displayBW();
		});
	};
</script>
JS
	puts js
end

def module_lp( language )
	l = {
		'jp' => {
			'mod_name' => "登録解除",
			'msg' => "ユーザー登録を解除する場合は、パスワードを入力し登録解除ボタンを押してください。",
			'password' => "パスワード",
			'release' => "登録解除",
			'thanks' => "ユーザー登録を解除しました。ご利用ありがとうございました。",
			'nguser' => "特殊アカウントは登録解除できません。"
		}
	}
	return l[language]
end