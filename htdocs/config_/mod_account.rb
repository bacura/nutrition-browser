# Nutorition browser 2020 Config module for acount 0.1.0 (2025/08/10)
#encoding: utf-8

require 'bcrypt'

@debug = false

def config_module( cgi, db )
	module_js()
	l = module_lp( db.user.language )
	step = cgi['step']

	res = db.query( "SELECT pass, mail, aliasu FROM #{$TB_USER} WHERE user=? AND cookie=?", false, [db.user.name, db.user.uid] )&.first
	if res
		aliasu = res['aliasu']
		mail = res['mail']
		pass = res['pass']
		language = res['language']
	end

	if step ==  'change'
		new_mail = cgi['new_mail']
		new_aliasu = cgi['new_aliasu']
		old_password = cgi['old_password']
		new_password1 = cgi['new_password1']
		new_password2 = cgi['new_password2']
		language = cgi['language']

		if pass == old_password || pass == ''
			mail = new_mail if new_mail.to_s != ''
			aliasu = new_aliasu if new_aliasu.to_s != ''
			if new_password1 == new_password2
				pass = new_password1 if new_password1.to_s != ''
			end

			# Updating acount information
			db.query( "UPDATE #{$TB_USER} SET pass=?, mail=?, aliasu=?, language=? WHERE user=? AND cookie=?", true, [pass, mail, aliasu, language, db.user.name, db.user.uid] )
		else
			puts "<span class='msg_small_red'>#{l[:no_save]}</span><br>"
		end

	elsif step ==  'tensei'
		tensei_code = "#{cgi['tensei1']}-#{cgi['tensei2']}-#{cgi['tensei3']}-#{cgi['tensei4']}-#{cgi['tensei5']}"
		res = db.query( "SELECT * FROM #{$TB_TENSEI} WHERE code=?", false, [tensei_code] )&.first
		if res && res['expd'] >= Date.today

			# Updating acount status
			db.query( "UPDATE #{$TB_USER} SET status=?, tensei=? WHERE user=? AND cookie=?", true, [res['status'], res['code'], db.user.name, db.user.uid] )
			puts "<span class='msg_small_red'>#{l[:tensei_exec]}</span><br>"

		elsif tensei_code == 'R-E-S-E-T'
			# Resetting acount status
			db.query( "UPDATE #{$TB_USER} SET status=1, tensei='' WHERE user=? AND cookie=?", true, [db.user.name, db.user.uid] )
			puts "<span class='msg_small_red'>#{l[:tensei_reset]}</span><br>"

		else
			puts "<span class='msg_small_red'>#{l[:tensei_error]}</span><br>"
		end
	end


  	option_language = ''
  	$LP.each do |e| option_language << "<option value='#{e}'>#{e}</option>" end

  	tensei_html = ''
  	if @accounts_general.include?( db.user.status )
	  	tensei_html = <<~TENSEI
		<hr>
		<div class='row'>
	    	<div class='col-2'>#{l[:tensei_code]}</div>
			<div class='col-4'>
				<input type="text" id="tensei1" size='4' maxlength='4'>&nbsp;-&nbsp;
				<input type="text" id="tensei2" size='4' maxlength='4'>&nbsp;-&nbsp;
				<input type="text" id="tensei3" size='4' maxlength='4'>&nbsp;-&nbsp;
				<input type="text" id="tensei4" size='4' maxlength='4'>&nbsp;-&nbsp;
				<input type="text" id="tensei5" size='4' maxlength='4'>
			</div>
			<div class='col-4'><button type="button" class="btn btn-danger btn-sm nav_button" onclick="accountCfgTensei( 'tensei' )">#{l[:tensei]}</button></div>
		</div>
		TENSEI
	end

	html = <<~HTML
    <div class="container">
    	<div class='row'>
	    	<div class='col-2'>#{l[:aliase]}</div>
			<div class='col-4'><input type="text" maxlength="60" id="new_aliasu" class="form-control login_input" value="#{aliasu}"></div>
		</div>

    	<div class='row'>
	    	<div class='col-2'>#{l[:mail]}</div>
			<div class='col-4'><input type="email" maxlength="60" id="new_mail" class="form-control login_input" value="#{mail}"></div>
		</div>

    	<div class='row'>
	    	<div class='col-2'>#{l[:new_pw]}</div>
			<div class='col-4'><input type="text" maxlength="30" id="new_password1" class="form-control login_input" placeholder="#{l[:char30]}"></div>
		</div>

    	<div class='row'>
	    	<div class='col-2'>#{l[:new_pw]}</div>
			<div class='col-4'><input type="text" maxlength="30" id="new_password2" class="form-control login_input" placeholder="#{l[:confirm]}"></div>
		</div>

    	<div class='row'>
	    	<div class='col-2'>#{l[:language]}</div>
	    	<div class='col-2'>
        		<select id="language" class="form-select">
        		#{option_language}
        		</select>
			</div>
		</div>
		<hr>

    	<div class='row'>
	    	<div class='col-2'>#{l[:password]}</div>
			<div class='col-4'><input type="password" id="old_password" class="form-control login_input" required></div>
		</div>

    	<div class='row'>
	    	<div class='col-2'></div>
			<div class='col-4'><button type="button" class="btn btn-warning btn-sm nav_button" onclick="accountCfg( 'change' )">#{l[:save]}</button></div>
		</div>

		#{tensei_html}
	</div>
HTML

	return html
end


def module_js()
	js = <<-"JS"
<script type='text/javascript'>

// Updating account information
var accountCfg = function( step ){
	let new_mail = '';
	let new_aliasu = '';
	let old_password = '';
	let new_password1 = '';
	let new_password2 = '';
	let language = '';

	if( step == 'change' ){
		new_mail = document.getElementById( "new_mail" ).value;
		new_aliasu = document.getElementById( "new_aliasu" ).value;
		old_password = document.getElementById( "old_password" ).value;
		new_password1 = document.getElementById( "new_password1" ).value;
		new_password2 = document.getElementById( "new_password2" ).value;
		language = document.getElementById( "language" ).value;
	}

	postLayer( "config.cgi", '', true, 'L1', { mod:'account', step, new_mail, new_aliasu, old_password, new_password1, new_password2, language });

	dl1 = true;
	dline = true;
	displayBW();
};

var accountCfgTensei = function( step ){
	tensei1 = document.getElementById( "tensei1" ).value;
	tensei2 = document.getElementById( "tensei2" ).value;
	tensei3 = document.getElementById( "tensei3" ).value;
	tensei4 = document.getElementById( "tensei4" ).value;
	tensei5 = document.getElementById( "tensei5" ).value;

	postLayer( "config.cgi", '', true, 'L1', { mod:'account', step, tensei1, tensei2, tensei3, tensei4, tensei5 });
}


</script>
JS
	puts js
end


# Language pack
def module_lp( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		'mod_name'	=> "アカウント",
		aliase: "二つ名",
		mail: "メールアドレス",
		new_pw: "新しいパスワード",
		char30: "30文字まで",
		confirm: "(確認)",
		language: "言語",
		password: "現在のパスワード",
		save: "保存",
		tensei: "転生する",
		tensei_code: "転生コード",
		tensei_exec: "転生が行われました。ブラウザをリロードしてください。",
		tensei_error: "無効な転生コードです。転生できません。",
		tensei_reset: "転生がリセットされました。ブラウザをリロードしてください。",
		no_save: "現在のパスワードが違うので、保存されませんでした。"
	}

	return l[language]
end
