#!/usr/bin/ruby
# encoding: utf-8
# Nutrition Browser 2020 regist 0.0.10 (2025/08/11)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
@myself = File.basename( __FILE__ )

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'

#==============================================================================
# DEFINITION
#==============================================================================

# Language Pack
def load_language_pack( language_code )
  l = {
    'jp' => {
      nb:        "栄養ブラウザ",
      login:     "ログイン",
      help:      "<img src='bootstrap-dist/icons/question-circle-ndsk.svg' style='height:2em; width:2em;'>",
      message:   "IDとパスワードは必須です。英数字とアンダーバー(_)のみ使用可能です。ご登録前に利用規約を確認しておいてください。",
      id_rule:   "ID (4~30文字)",
      pass_rule: "パスワード (30文字まで)",
      a_rule:    "二つ名 (60文字まで)",
      mail_rule: "メールアドレス (60文字まで)",
      submit:    "送信",
      error1:    "入力されたIDは英数字とハイフン、アンダーバー以外の文字が使用されています。別のIDを入力して登録してください。",
      error2:    "入力されたIDは制限の30文字を越えています。別のIDを入力して登録してください。",
      error3:    "IDは4文字以上の長さが必要です。別のIDを入力して登録してください。",
      error4:    "入力されたIDはすでに使用されています。別のIDを入力して登録してください。",
      confirm:   "下記の内容でよろしければ登録してください。",
      id:        "ID",
      aliase:    "二つ名",
      mail:    "メールアドレス",
      pass:      "パスワード",
      language:  "言語",
      regist:    "登録する",
      back:      "変更する",
      thanks:    "ご登録ありがとうございました。",
      thanks2:   "して引き続きご利用ください。"
    }
  }
  return l[language_code]
end

# HTML Header
def render_html_top( l )
  login_button = "<a href='login.cgi' class=\"text-secondary\">#{l[:login]}</a>"

  html_output = <<-"HTML"
<header class="navbar navbar-expand-lg navbar-dark bg-dark" id="header">
  <div class="container-fluid">
    <a href="index.cgi" class="navbar-brand h1 text-secondary">#{l[:nb]}</a>
    <span class="navbar-text text-secondary login_msg h4">#{login_button}</span>
    <a href='https://bacura.jp/?page_id=543' target='manual'>#{l[:help]}</a>
  </div>
</header>
HTML

  puts html_output
end

# HTML Registration Form
def render_registration_form( id, mail, pass, msg, aliasu, l )
  language_options = $LP.map { |e| "<option value='#{e}'>#{e}</option>" }.join

  html_output = <<-"HTML"
    <div class="container">
      <form action="#{@myself}?mode=confirm" method="post" class="form-signin login_form">
        #{msg}
        <p class="msg_small">#{l[:message]}</p>
        <input type="text" name="id" value="#{id}" maxlength="30" class="form-control login_input" placeholder="#{l[:id_rule]}" required autofocus>
        <input type="text" name="pass" value="#{pass}" maxlength="30" class="form-control login_input" placeholder="#{l[:pass_rule]}" required>
        <input type="text" name="aliasu" value="#{aliasu}" maxlength="60" class="form-control login_input" placeholder="#{l[:a_rule]}">
        <input type="email" name="mail" value="#{mail}" maxlength="60" class="form-control login_input" placeholder="#{l[:mail_rule]}">
        <select name="language" class="form-select">
          #{language_options}
        </select>
        <br>
        <input type="submit" value="#{l[:submit]}" class="btn btn-success btn-block"></input>
      </form>
    </div>

    <hr>
    <div class="container" id='rule'></div>
    <script>$( function(){ $( "#rule" ).load( "books/guide/rule.html" );} );</script>
HTML

  puts html_output
end

# HTML Registration Confirmation
def render_registration_confirmation( id, mail, pass, aliasu, language, l )
  html_output = <<-"HTML"
    <div class="container">
      <form action="#{@myself}?mode=finish" method="post" class="form-signin login_form">
        <p class="msg_small">#{l[:confirm]}</p>
        <table class="table">
          <tr>
            <td>#{l[:id]}</td>
            <td>#{id}</td>
          </tr>
          <tr>
            <td>#{l[:pass]}</td>
            <td>#{pass}</td>
          </tr>
          <tr>
            <td>#{l[:aliase]}</td>
            <td>#{aliasu}</td>
          </tr>
          <tr>
            <td>#{l[:mail]}</td>
            <td>#{mail}</td>
          </tr>
          <tr>
            <td>#{l[:language]}</td>
            <td>#{language}</td>
          </tr>
        </table>
        <input type="hidden" name="id" value="#{id}">
        <input type="hidden" name="aliasu" value="#{aliasu}">
        <input type="hidden" name="mail" value="#{mail}">
        <input type="hidden" name="pass" value="#{pass}">
        <input type="hidden" name="language" value="#{language}">
        <input type="submit" value="#{l[:regist]}" class="btn btn-warning btn-block"></input>
        <input type="button" value="#{l[:back]}" class="btn btn-secondary btn-block" onclick="history.back()"></input>
      </form>
    </div>
HTML

  puts html_output
end

# HTML Registration Finish
def render_registration_finish( l )
  html_output = <<-"HTML"
    <div class="container">
      <p class="reg_msg">#{l[:thanks]}<a href="login.cgi">#{l[:login]}<a/>#{l[:thanks2]}</p>
    </div>
HTML

  puts html_output
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.status = 0 unless user.name
l = load_language_pack( $DEFAULT_LP )
db = Db.new( user, @debug, false )

request_data = get_data()

html_head( nil, 0, nil )
render_html_top( l )

p request_data['mode'] if @debug
case request_data['mode']
when 'confirm'
  if /[^0-9a-zA-Z\_]/ =~ @cgi['id']
    error_message = "<p class='msg_small_red'>#{l[:error1]}</p>"
    render_registration_form( nil, @cgi['mail'], nil, error_message, @cgi['aliasu'], l )

  elsif @cgi['id'].size > 30
    error_message = "<p class='msg_small_red'>#{l[:error2]}</p>"
    render_registration_form( nil, @cgi['mail'], nil, error_message, @cgi['aliasu'], l )

  elsif @cgi['id'].size < 4
    error_message = "<p class='msg_small_red'>#{l[:error3]}</p>"
    render_registration_form( nil, @cgi['mail'], nil, error_message, @cgi['aliasu'], l )

  else
    res = db.query( "SELECT user FROM #{$MYSQL_TB_USER} WHERE user=?", false, [@cgi['id']] )&.first
    if res
      p true if @debug
      error_message = "<p class='msg_small_red'>#{l[:error4]}</p>"
      render_registration_form( nil, @cgi['mail'], nil, error_message, @cgi['aliasu'], l )

    else
      p false if @debug
      render_registration_confirmation( @cgi['id'], @cgi['mail'], @cgi['pass'], @cgi['aliasu'], @cgi['language'], l )
    end
  end

when 'finish'
  aliasu = @cgi['aliasu'].empty? ? @cgi['id'] : @cgi['aliasu']
  p @cgi if @debug

  db.query( "INSERT INTO #{$MYSQL_TB_USER} SET user=?, mail=?, pass=?, aliasu=?, status=1, language=?, reg_date=?", true, @cgi['id'], @cgi['mail'], @cgi['pass'], aliasu, @cgi['language'], @datetime )

  # Inserting standard palettes
  3.times do |c|
    db.query( "INSERT INTO #{$MYSQL_TB_PALETTE} SET user=?, name=?, palette=?", true, [@cgi['id'], @palette_default_name[c], @palette_default[c]] )
  end

  db.query( "INSERT INTO #{$MYSQL_TB_HIS} SET user=?, his='';", true, [@cgi['id']] )
  db.query( "INSERT INTO #{$MYSQL_TB_SUM} SET user=?, sum='';", true, [@cgi['id']] )
  db.query( "INSERT INTO #{$MYSQL_TB_MEAL} SET user=?, meal='';", true, [@cgi['id']] )
  db.query( "INSERT INTO #{$MYSQL_TB_CFG} SET user=?, icache=1;", true, [@cgi['id']] )

  render_registration_finish( l )
else
  render_registration_form( nil, nil, nil, nil, nil, l )

end

html_foot()
