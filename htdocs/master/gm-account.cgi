#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 GM account editor 0.0.2 (2026/01/04)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'
require 'bcrypt'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		pass:	"パス",
		mail:	"メール",
		alias:	"二つ名",
		status:	"ステータス",
		language:	"言語",
		save:	"保存",
		user:	"ユーザー",
		final:	"最終",
		regist:	"登録",
		count:	"カウント",
		edit:	"編集",
		acount_edit:	"アカウントエディタ"
	}

	return l[language]
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )


#### GM check
if user.status < 9
	puts "GM error."
	exit
end


#### Getting POST data
command = @cgi['command']
target_uid = @cgi['target_uid']
target_pass = @cgi['target_pass']
target_mail = @cgi['target_mail']
target_aliasu = @cgi['target_aliasu']
target_status = @cgi['target_status']
target_language = @cgi['target_language'].to_i
if @debug
	puts "command:#{command}<br>\n"
	puts "target_uid:#{target_uid}<br>\n"
	puts "target_pass:#{target_pass}<br>\n"
	puts "target_mail:#{target_mail}<br>\n"
	puts "target_aliasu:#{target_aliasu}<br>\n"
	puts "target_status:#{target_status}<br>\n"
	puts "target_language:#{target_language}<br>\n"
	puts "<hr>\n"
end


account_html = ''
if command == 'edit'
	res = db.query( "SELECT * FROM #{$TB_USER} WHERE user=?", false, [target_uid] )&.first
	if res
		account_html << "<div class='row'>"
		account_html << "	<div class='col-1'>#{l[:pass]}</div><div class='col-4'><input type='text' class='form-control' id='target_pass' value='#{res['pass']}'></div>"
		account_html << "</div><br>"
		account_html << "<div class='row'>"
		account_html << "	<div class='col-1'>#{l[:mail]}</div><div class='col-4'><input type='text' class='form-control' id='target_mail' value='#{res['mail']}'></div>"
		account_html << "</div><br>"
		account_html << "<div class='row'>"
		account_html << "	<div class='col-1'>#{l[:alias]}</div><div class='col-4'><input type='text' class='form-control' id='target_aliasu' value='#{res['aliasu']}'></div>"
		account_html << "</div><br>"
		account_html << "<div class='row'>"
		account_html << "	<div class='col-1'>#{l[:status]}</div>"
		account_html << "	<div class='col-4'>"
		account_html << "<select class='form-select' id='target_status'>"

		10.times do |c| account_html << "<option value='#{c}' #{$SELECT[res['status'].to_i == c]}>#{@account[c]}</option>" end

		account_html << "</select>"
		account_html << "</div>"
		account_html << "</div><br>"
		account_html << "<div class='row'>"
		account_html << "	<div class='col-1'>#{l[:language]}</div>"
		account_html << "	<div class='col-4'>"
		account_html << "		<select class='form-select' id='target_language'>"

		$LP.each do |e| account_html << "<option value='#{e}' #{$SELECT[res['lp'] == e]}>#{e}</option>" end

		account_html << "		</select>"
		account_html << "	</div>"
		account_html << "</div><br>"
		account_html << "<div class='row'>"
		account_html << "	<div class='col-5' align='center'><button type='button' class='btn btn-success btn-sm nav_button' onclick=\"saveAccount( '#{target_uid}' )\">#{l[:save]}</button></div>"
		account_html << "</div>"
	end
else
	if command == 'save'
		if target_pass.empty?
			db.query( "UPDATE #{$TB_USER} SET mail=?, aliasu=?, status=?, language=? WHERE user=?", true, [target_mail, target_aliasu, target_status, $LP[target_language], target_uid] )
		else
  			passh = BCrypt::Password.create( target_pass )
			db.query( "UPDATE #{$TB_USER} SET passh=?, mail=?, aliasu=?, status=?, language=? WHERE user=?", true, [passh, target_mail, target_aliasu, target_status, $LP[target_language], target_uid] )
		end
	end

	account_html << "<div class='row'>"
	r = db.query( "SELECT * FROM #{$TB_USER} WHERE status!='9' AND user!='';", false )
	if r.first
		account_html << "<table class='table table-striped table-bordered'>"
		account_html << "<thead>"
		account_html << "<th>#{l[:user]}</th>"
		account_html << "<th>#{l[:mail]}</th>"
		account_html << "<th>#{l[:alias]}</th>"
		account_html << "<th>#{l[:status]}</th>"
		account_html << "<th>#{l[:final]}</th>"
		account_html << "<th>#{l[:regist]}</th>"
		account_html << "<th>#{l[:count]}</th>"
		account_html << "<th>#{l[:language]}</th>"
		account_html << "</thead>"

		r.each do |e|
			account_html << "<tr>"
			account_html << "<td>#{e['user']}</td>"
			account_html << "<td>#{e['mail']}</td>"
			account_html << "<td>#{e['aliasu']}</td>"
			account_html << "<td>#{@account[e['status'].to_i]}</td>"
			account_html << "<td>#{e['login_date']}</td>"
			account_html << "<td>#{e['reg_date']}</td>"
			account_html << "<td>#{e['count']}</td>"
			account_html << "<td>#{e['language']}</td>"
			account_html << "<td><button type='button' class='btn btn-success btn-sm nav_button' onclick='editAccount( \"#{e['user']}\" )'>#{l[:edit]}</button></td>"
			account_html << "</tr>"
		end

		account_html << "</table>"
	else
		account_html << 'no account.'
	end
end

html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col'><h5>#{l[:acount_edit]}: #{target_uid}</h5></div>
	</div>
	#{account_html}
</div>
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================


#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

// Edit account
var editAccount = ( target_uid ) => {
	postLayer( mp + '#{myself}', 'edit', true, 'L2', { target_uid });

	dl2 = true;
	displayBW();
};

// Update account
var saveAccount = ( target_uid ) => {
	const target_pass = document.getElementById( 'target_pass' ).value;
	const target_mail = document.getElementById( 'target_mail' ).value;
	const target_aliasu = document.getElementById( 'target_aliasu' ).value;
	const target_status = document.getElementById( 'target_status' ).value;
	const target_language = document.getElementById( 'target_language' ).value;

	postLayer( mp + '#{myself}', 'save', true, 'L1', { target_uid, target_pass, target_mail, target_aliasu, target_status, target_language });

	dl2 = true;
	dl2 = false;
	displayBW();
	displayVIDEO( target_uid + ' saved' );
};

</script>

JS

	puts js
end
