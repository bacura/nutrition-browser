# Nutorition browser 2020 Config module for release 0.0.3 (26/01/02)
#encoding: utf-8

# Debug mode
@debug = false

def config_module( cgi, db )
	module_js()
	l = module_lp( db.user.language )
	step = cgi['step']

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

			db.query( "UPDATE #{$TB_USER} SET status='0' WHERE user=? AND cookie=?", true, [db.user.name, db.user.uid] )
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
				#{l[:msg]}<br>
			</div><br>
			<div class='row'>
				<div class='col-4'><input type="password" id="password" class="form-control form-control-sm login_input" placeholder="#{l[:password]}" required></div>
				<div class='col-4'><button type="button" class="btn btn-outline-danger btn-sm nav_button" onclick="release_cfg()">#{l[:release]}</button></div>
			</div>
		</div>
	HTML
end

def render_general_release( l )
	<<-"HTML"
		<div class="container">
			<div class='row'>
				#{l[:thanks]}
			</div>
		</div>
	HTML
end


def delete_user_data( db )
	[
		$TB_HIS, 
		$TB_SUM, 
		$TB_CFG, 
		$TB_MEAL,
		$TB_PRICEM, 
		$TB_PALETTE
	].each do |table|
		db.query( "DELETE FROM #{table} WHERE user=?", true, [db.user.name] )
	end
end

def render_rom_release( l )
	<<-"HTML"
		<div class="container">
			<div class='row'>
				#{l[:nguser]}
			</div> 
		</div>
	HTML
end

def module_js()
	js = <<-"JS"
<script type='text/javascript'>
	var release_cfg = function(){
		const password = document.getElementById( "password" ).value;
		postLayer( "config.cgi", '', true, 'L1', { mod:'release', step:'release', password });

		flashBW();
		dl1 = true;
		dline = true;
		displayBW();
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
		'mod_name'	=> "登録解除",
		msg:	"ユーザー登録を解除する場合は、パスワードを入力し登録解除ボタンを押してください。",
		password:	"パスワード",
		release:	"登録解除",
		thanks:	"ユーザー登録を解除しました。ご利用ありがとうございました。",
		nguser:	"特殊アカウントは登録解除できません。"

	}

	return l[language]
end
