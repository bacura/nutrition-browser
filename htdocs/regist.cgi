#!/usr/bin/ruby
# encoding: utf-8
# Nutrition Browser 2020 regist 0.1.0 (2026/02/11)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
@myself = File.basename( __FILE__ )

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require 'bcrypt'
require 'net/smtp'
require 'uri'

#==============================================================================
# DEFINITION
#==============================================================================

# Language Pack
def load_language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    login:     "ログイン",
    help:      "<img src='bootstrap-dist/icons/question-circle-ndsk.svg' style='height:2em; width:2em;'>",
    message:   "IDとパスワードは必須です。英数字とアンダーバー(_)のみ使用可能です。ご登録前に利用規約を確認しておいてください。",
    message_reset:   "<p>IDと登録メールアドレスを入力してください。パスワード再設定用のURLを登録メールアドレス宛に送信します。</p><p>IDがわからない方、もしくはメールアドレスが未登録の方は残念ながら詰です。念のため、管理者にコンタクトをとってみましょう。</p>",
    message_send:   "パスワード再設定用のURLを登録メールアドレス宛に送信しました。そこから新しいパスワードを設定してください。（メールが届かない場合は迷惑メールフォルダも確認してください）",
    message_link_out:   "リンクが無効か期限切れです。もう一度パスワード再設定用のURLを登録メールアドレス宛に送信してください。",
    message_reset_npw:   "新しいパスワードを設定してください。",
    message_feel_wrong:   "なにか間違っている気がします。",
    message_id_no:   "ユーザーIDを入力してください。",
    message_pass_no:   "新しいパスワードと確認用パスワードの両方を入力してください。",
    message_pass_nm:   "新しいパスワードと確認用パスワードが一致しません。",
    message_pass_30:   "パスワードは30文字以内にしてください。",
    message_crazy:   "操作に狂気を感じましたので",
    message_lock_up:   "は封印されました。念のため、管理者にコンタクトをとってみましょう。",
    message_reseted:  "パスワードを再設定しました。",
    message_to_login: "ログイン画面へ",
    mail_subject: "栄養ブラウザ　パスワード再設定",
    mail_body1: "このメールは栄養ブラウザのパスワード再設定リクエストを受けて送信されました。",
    mail_body2: "お心当たりがない場合は、このメールを無視してください。",
    mail_body3: "以下のリンクをクリックして、新しいパスワードを設定してください。",
    mail_body4: "なお、このリンクの有効期限は20分です。",
    mail_body5: "また、このメールに返信しても何も起こりません。",
    mail_body6: "〔ばきゅら京都Lab　管理人〕",
    id_rule:   "ID (8~30文字)",
    id_reset:   "ID",
    pass_rule: "パスワード (30文字まで)",
    pw1_reset: "新しいパスワード (30文字まで)",
    pw2_reset: "新しいパスワード（確認用）",
    a_rule:    "二つ名 (60文字まで)",
    mail_rule: "メールアドレス (60文字まで。大文字は小文字に変換されます。)",
    mail_reset: "登録メールアドレス",
    submit:    "送信",
    submit_npw:    "再設定",
    error1:    "入力されたIDは英数字とハイフン、アンダーバー以外の文字が使用されています。別のIDを入力して登録してください。",
    error2:    "入力されたIDは制限の30文字を越えています。別のIDを入力して登録してください。",
    error3:    "IDは8文字以上の長さが必要です。別のIDを入力して登録してください。",
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
    thanks2:   "して引き続きご利用ください。",
  }

  return l[language]
end

# HTML Header
def render_html_top( l )
  login_button = "<a href='login.cgi' class=\"text-secondary\">#{l[:login]}</a>"

  html_output = <<-"HTML"
<header class="navbar navbar-expand-lg navbar-dark bg-dark" id="header">
  <div class="container-fluid">
    <a href="index.cgi" class="navbar-brand h1 text-secondary">#{@title}</a>
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
        <input type="password" name="pass" value="#{pass}" maxlength="30" class="form-control login_input" placeholder="#{l[:pass_rule]}" required>
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

# HTML Reset Form
def render_reset_form( msg, id, mail, l )
  html_output = <<~HTML
    <div class="container">
      <form action="#{@myself}?mode=send_reset_mail" method="post" class="form-signin login_form">
        <p class="msg_small">#{msg}</p>
        <input type="text" name="id_reset" value="#{id}" maxlength="30" class="form-control login_input" placeholder="#{l[:id_reset]}" required autofocus>
        <input type="email" name="mail_reset" value="#{mail}" maxlength="60" class="form-control login_input" placeholder="#{l[:mail_reset]}" required>
        <br>
        <input type="submit" value="#{l[:submit]}" class="btn btn-success btn-block"></input>
      </form>
    </div>
HTML

  puts html_output
end


def send_reset_email( mail, token, id, l )
  link = "#{$HTDOCS_PATH}/#{@myself}?mode=reset_receive&token=#{URI.encode_www_form_component( token )}"

  subject = l[:mail_subject]
  body = <<~TEXT
    #{mail_body1}

    #{mail_body2}

    #{mail_body3}

    #{link}

    #{mail_body4}
    #{mail_body5}
    #{mail_body6}
  TEXT

  message = <<~EOF
    From: #{$FROM_EMAIL}
    To: #{mail}
    Subject: #{subject}
    MIME-Version: 1.0
    Content-Type: text/plain; charset=UTF-8

    #{body}
  EOF

  smtp = Net::SMTP.new($SMTP_SERVER, $SMTP_PORT)
  smtp.enable_starttls_auto  # TLS有効

  smtp.start('localhost', $SMTP_USER, $SMTP_PASS, :plain) do |smtp_conn|
    smtp_conn.send_message(message, $FROM_EMAIL, mail)
  end

  puts "[INFO] Reset email sent to #{mail}" if @debug
rescue => e
  puts "[ERROR] SMTP send failed: #{e.message}" if @debug
end


# HTML Reset Mail
def render_reset_mail( cgi, db, l )
  id   = ( cgi['id_reset'] || '' ).strip
  mail = ( cgi['mail_reset'] || '' ).strip.downcase

  res = db.query( "SELECT * FROM #{$TB_USER} WHERE user=? AND mail=? LIMIT 1", false, [id, mail] )&.first
  if res && id != $GM && id.size <= 30 && id.size >= 8 && res['status'].to_i > 0
    token = SecureRandom.urlsafe_base64( 32 )
    expires_at = ( Time.now + 1200 ).strftime( '%Y-%m-%d %H:%M:%S' )
    db.query( "UPDATE #{$TB_USER} SET reset_token = ?, reset_token_expires_at=? WHERE user=?", true, [token, expires_at, id] )

    send_reset_email(mail, token, id, l)
  end

  render_reset_form( l[:message_send], '', '', l )
end

# HTML Reset Receive Form
def render_reset_receive_form( msg, token, l )
  html_output = <<~HTML
    <div class="container">
      <form action="#{@myself}?mode=reset_finish" method="post" class="form-signin login_form">
        <p class="msg_small">#{msg}</p>
        <input type="text" name="id_reset" value="" maxlength="30" class="form-control login_input" placeholder="#{l[:id_reset]}" required autofocus>
        <input type="password" name="new_pass_reset1" value="" maxlength="30" class="form-control login_input" placeholder="#{l[:pw1_reset]}" required>
        <input type="password" name="new_pass_reset2" value="" maxlength="30" class="form-control login_input" placeholder="#{l[:pw2_reset]}" required>
        <input type="hidden" name="token" value="#{token}">
        <br>
        <input type="submit" value="#{l[:submit_npw]}" class="btn btn-success btn-block"></input>
      </form>
    </div>
HTML

  puts html_output
end

# HTML Reset Finish
def render_reset_finish( cgi, db, l )
  user = ( cgi['id_reset'] || '' ).strip
  token  = ( cgi['token'] || '' ).strip
  pass1  = ( cgi['new_pass_reset1'] || '' ).strip
  pass2  = ( cgi['new_pass_reset2'] || '' ).strip

  # 入力チェック
  if user.empty?
    msg = "<p class='msg_small_red'>#{l[:message_id_no]}</p>"
    render_reset_receive_form( msg, token, l )
    return
  end

  if pass1.empty? || pass2.empty?
    msg = "<p class='msg_small_red'>#{l[:message_pass_no]}</p>"
    render_reset_receive_form( msg, token, l )
    return
  end

  if pass1 != pass2
    msg = "<p class='msg_small_red'>#{l[:message_pass_nm]}</p>"
    render_reset_receive_form( msg, token, l )
    return
  end

  if pass1.size > 30
    msg = "<p class='msg_small_red'>#{l[:message_pass_30]}</p>"
    render_reset_receive_form( msg, token, l )
    return
  end

  # トークン再検証（必須）
  res = db.query( "SELECT user FROM #{$TB_USER} WHERE user=? AND status>0 AND reset_token=? AND reset_token_expires_at > NOW() LIMIT 1", false, [user, token] )&.first
  if !res
    res2 = db.query( "SELECT user, reset_count FROM #{$TB_USER} WHERE reset_token=? LIMIT 1", false, [token] )&.first
    if res2
      reset_count = res2['reset_count'].to_i
      if reset_count == 20
        db.query( "UPDATE #{$TB_USER} SET status=0, reset_token=NULL, reset_token_expires_at=NULL, reset_count=0 WHERE user=?", true, [user] )
        puts "#{l[:message_crazy]}#{res2['user']}#{l[:message_lock_up]}"
      elsif ( reset_count % 5 ) == 4
        reset_count += 1
        db.query( "UPDATE #{$TB_USER} SET reset_token=NULL, reset_token_expires_at=NULL, reset_count=? WHERE user=?", true, [reset_count, user] )
        render_reset_form( "<p class='msg_small_red'>#{l[:message_feel_wrong]}</p>", '', '', l )
      else
        render_reset_form( "<p class='msg_small_red'>#{l[:message_feel_wrong]}</p>", '', '', l )
      end
    else
      render_reset_form( "<p class='msg_small_red'>#{l[:message_feel_wrong]}</p>", '', '', l )
    end

    return
  end

# パスワード更新
  passh = BCrypt::Password.create( pass1 )
  db.query( "UPDATE #{$TB_USER} SET passh=?, reset_token=NULL, reset_token_expires_at=NULL, reset_count=0 WHERE user=?", true, [passh, user] )

  html_output = <<~HTML
  <div class="container">
    <p class="msg_small success">#{l[:message_reseted]}</p>
    <p><a href="login.cgi" class="btn btn-primary">#{l[:message_to_login]}</a></p>
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
  aliasu = @cgi['aliasu'].empty? ? @no_aliase : @cgi['aliasu']
  mail = @cgi['mail']&.strip.downcase
  mail ||= ''

  if /[^0-9a-zA-Z\_]/ =~ @cgi['id']
    error_message = "<p class='msg_small_red'>#{l[:error1]}</p>"
    render_registration_form( nil, mail, nil, error_message, aliasu, l )

  elsif @cgi['id'].size > 30
    error_message = "<p class='msg_small_red'>#{l[:error2]}</p>"
    render_registration_form( nil, mail, nil, error_message, aliasu, l )

  elsif @cgi['id'].size < 8
    error_message = "<p class='msg_small_red'>#{l[:error3]}</p>"
    render_registration_form( nil,mail, nil, error_message, aliasu, l )

  else
    res = db.query( "SELECT user FROM #{$TB_USER} WHERE user=?", false, [@cgi['id']] )&.first
    if res
      p true if @debug
      error_message = "<p class='msg_small_red'>#{l[:error4]}</p>"
      render_registration_form( nil, mail, nil, error_message, aliasu, l )

    else
      p false if @debug
      render_registration_confirmation( @cgi['id'], mail, @cgi['pass'], aliasu, @cgi['language'], l )
    end
  end

when 'finish'
  p @cgi if @debug

  aliasu = @cgi['aliasu'].empty? ? @no_aliase : @cgi['aliasu']
  mail = @cgi['mail']&.strip.downcase
  mail ||= ''

  passh = BCrypt::Password.create( @cgi['pass'] )
  db.query( "INSERT INTO #{$TB_USER} SET user=?, mail=?, passh=?, aliasu=?, status=1, language=?, reg_date=?", true, [@cgi['id'], mail, passh, aliasu, @cgi['language'], @datetime] )

  # Inserting standard palettes
  3.times do |c|
    db.query( "INSERT INTO #{$TB_PALETTE} SET user=?, name=?, palette=?", true, [@cgi['id'], @palette_default_name[c], @palette_default[c]] )
  end

  db.query( "INSERT INTO #{$TB_HIS} SET user=?, his='';", true, [@cgi['id']] )
  db.query( "INSERT INTO #{$TB_SUM} SET user=?, sum='';", true, [@cgi['id']] )
  db.query( "INSERT INTO #{$TB_MEAL} SET user=?, meal='';", true, [@cgi['id']] )
  db.query( "INSERT INTO #{$TB_CFG} SET user=?, icache=1;", true, [@cgi['id']] )

  render_registration_finish( l )

when 'reset_form'
  render_reset_form( l[:message_reset], '', '', l )

when 'send_reset_mail'
  render_reset_mail( @cgi, db, l )

when 'reset_receive'
  token = ( request_data['token'] || @cgi['token'] || '' ).strip
  if token.empty?
      render_reset_form( "<p class='msg_small_red'>#{l[:message_link_out]}</p>", '', '', l )
  else
    res = db.query( "SELECT user, mail FROM #{$TB_USER} WHERE reset_token = ? AND reset_token_expires_at > NOW() LIMIT 1", false, [token] )&.first
    if res
      render_reset_receive_form( l[:message_reset_npw], token, l )
    else
      render_reset_form( "<p class='msg_small_red'>#{l[:message_link_out]}</p>", '', '', l )
    end
  end

when 'reset_finish'
  render_reset_finish( @cgi, db, l )

else
  render_registration_form( nil, nil, nil, nil, nil, l )

end

html_foot()
