#! /usr/bin/ruby
# coding: utf-8
# Nutrition browser 2020 login 0.2.0 (2026/03/01)

#==============================================================================
# STATIC
#==============================================================================
@debug = false

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require 'bcrypt'

#==============================================================================
# METHODS
#==============================================================================

# Language pack
def language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    message:  "IDとパスワードを入力してログインしてください。",
    password: "パスワード",
    login:    "ログイン",
    error:    "IDとパスワードが一致しませんでした。<br>パスワードを忘れた方は再登録してください。",
    help:     "<img src='bootstrap-dist/icons/question-circle-ndsk.svg' style='height:3em; width:2em;'>",
    regist:   "登録",
    reset:   "パスワードを忘れた方は<a href='regist.cgi?mode=reset_form'>こちら</a>",
    empty:    "[空き地]"
  }

  return l[language]
end

def render_html( content )
  puts content
end

def render_login_form( msg, l )
  reset_form = ( $SMTP_SERVER.to_s.empty? || $SMTP_SERVER == '--smtp--' ) ? '' : l[:reset]

  form_html = <<-"HTML"
    <div class="container">
      <div class="row">
        <div class="col-6">
          <form action="login.cgi?mode=check" method="post" class="form-signin login_form">
            #{msg}
            <p class="msg_small">#{l[:message]}</p>
            <input type="text" name="id" id="inputID" class="form-control login_input" placeholder="ID" required autofocus>
            <input type="password" name="pass" id="inputPassword" class="form-control login_input" placeholder="#{l[:password]}">
            <input type="submit" value="#{l[:login]}" class="btn btn-primary btn-block"></input>
          </form>
        </div>
        <div class="col-6">
          #{l[:empty]}
        </div>
      </div>
      <hr>
      <div class="row">
        <div class="col-6">
          #{reset_form}
        </div>
      </div>
    </div>
  HTML
  render_html( form_html )
end

def render_top_login( l )
  top_login_html = <<-"HTML"
    <header class="navbar navbar-expand-lg navbar-dark bg-dark" id="header">
      <div class="container-fluid">
        <a href="index.cgi" class="navbar-brand h1 text-secondary">#{@title}</a>
        <span class="navbar-text text-secondary login_msg h4"><a href="regist.cgi" class="text-secondary">#{l[:regist]}</a></span>
        <a href='https://bacura.jp/?page_id=543' target='manual'>#{l[:help]}</a>
      </div>
    </header>
  HTML
  render_html( top_login_html )
end

def validate_user( db, cgi, l )
  res = db.query( "SELECT user, passh, status, cookie FROM #{$TB_USER} WHERE user=? AND status>'0'", false, [cgi['id']] )&.first
  #for initial empty password

  if res
    if res['passh'].empty? && cgi['pass'].empty?
      update_user_data( db, res, cgi )

    elsif !cgi['pass'].empty? && res['passh'].empty?
      html_init( nil )
      html_head( nil, 0, nil )
      render_top_login( l )
      render_login_form( "<p class='msg_small_red'>#{l[:error]}</p>", l )
      html_foot()

    elsif BCrypt::Password.new( res['passh'] ) == cgi['pass']
      update_user_data( db, res, cgi )

    else
      html_init( nil )
      html_head( nil, 0, nil )

      render_top_login( l )
      render_login_form( "<p class='msg_small_red'>#{l[:error]}</p>", l )
      html_foot()
    end
  else
      html_init( nil )
      html_head( nil, 0, nil )
      render_top_login( l )
      render_login_form( "<p class='msg_small_red'>#{l[:error]}</p>", l )
      html_foot()
  end
end

def update_user_data( db, user_data, cgi )
  status = user_data['status'].to_i
  uid = SecureRandom.hex( 16 )
  cookie = "Set-Cookie: NAME=#{cgi['id']}\nSet-Cookie: #{$COOKIE_UID}=#{uid}\n"

  db.query( "UPDATE #{$TB_USER} SET cookie=?, cookie_m=NULL WHERE user=?", true, [uid, cgi['id']] )
  html_init( cookie )
  html_head( 'refresh', status, nil )
  puts '</span></body></html>'

  initialize_user_config( db, cgi, status ) unless status == 7
end

def initialize_user_config( db, cgi, status )
  res = db.query( "SELECT user FROM #{$TB_HIS} WHERE user=?", false, [cgi['id']] )&.first
  db.query( "INSERT INTO #{$TB_HIS} SET user=?, his='';", true, [cgi['id']] ) unless res

  res = db.query( "SELECT user FROM #{$TB_SUM} WHERE user=?", false, [cgi['id']] )&.first
  db.query( "INSERT INTO #{$TB_SUM} SET user=?, sum='';", true, [cgi['id']] ) unless res

  res = db.query( "SELECT user FROM #{$TB_MEAL} WHERE user=?", false, [cgi['id']] )&.first
  db.query( "INSERT INTO #{$TB_MEAL} SET user=?, meal='';", true, [cgi['id']] ) unless res
end

def handle_family_login( db, get_data )
  login_mv_user = get_data['login_mv']
  pre_res = db.query( "SELECT * FROM #{$TB_USER} WHERE user=?", false, [login_mv_user] )&.first

  if pre_res
    if pre_res['mom'].to_s.empty?
      # 娘→母親への切り替え
      cookie_m = db.user.mid
      if cookie_m.to_s.empty?
        html_init( nil )
        puts 'No(x_x)MOM'
        exit
      end

      mom_res = db.query( "SELECT * FROM #{$TB_USER} WHERE cookie=? AND user=?", false, [cookie_m, login_mv_user] )&.first
      if mom_res.nil?
        html_init( nil )
        puts 'No(x_x)MOM'
        exit
      end

      cookie = "Set-Cookie: NAME=#{mom_res['user']}\nSet-Cookie: #{$COOKIE_UID}=#{cookie_m}\n"
      html_init( cookie )
      html_head( 'refresh', mom_res['status'], nil )
      puts '</span></body></html>'

    else
      # 母親→娘への切り替え
      cookie = handle_family_cookie( db, pre_res )
      html_init( cookie )
      html_head( 'refresh', pre_res['status'], nil )
      puts '</span></body></html>'
    end

    db.query( "UPDATE #{$TB_USER} SET cookie_m=NULL WHERE user=?", true, [db.user.name] )

  else
    html_init( nil )
    puts 'No(x_x)FU'
    exit
  end
end

def handle_family_cookie( db, pre_res )
  post_res = db.query( "SELECT * FROM #{$TB_USER} WHERE user=?", false, [pre_res['mom']] )&.first
  return unless post_res

  uid = pre_res['cookie']
#  uid = SecureRandom.hex( 16 )

  parent_cookie = post_res['cookie']

  db.query( "UPDATE #{$TB_USER} SET cookie=?, cookie_m=? WHERE user=?", true, [uid, parent_cookie, pre_res['user']] )
  return "Set-Cookie: NAME=#{pre_res['user']}\nSet-Cookie: #{$COOKIE_UID}=#{uid}\n"
end

#==============================================================================
# MAIN
#==============================================================================
html_init( nil ) if @debug

get_data = get_data()
user = User.new( @cgi )
l = language_pack( user.language )
if l.nil?
  html_init( nil )
  puts 'U(x_x)L'
  exit
end
db = Db.new( user, false, true )

p get_data['mode'] if @debug
case get_data['mode']
when 'check'
  validate_user( db, @cgi, l )

when 'logout'
  cookie = "Set-Cookie: NAME=NULL\nSet-Cookie: #{$COOKIE_UID}=NULL\n"
  html_init( cookie )
  html_head( 'refresh', 0, nil )
  puts '</span></body></html>'
  db.query( "UPDATE #{$TB_USER} SET cookie_m=NULL WHERE user=?", true, [user.name] )

when 'family'
  handle_family_login( db, get_data )

else
  # ブラウザのcookieをDBと照合
  browser_uid = @cgi.cookies[$COOKIE_UID]&.first
  if browser_uid && !browser_uid.empty?
    res = db.query( "SELECT * FROM #{$TB_USER} WHERE cookie=?", false, [browser_uid] )&.first
    if res
      # 一致したらそのままリダイレクト
      html_init( nil )
      html_head( 'refresh', res['status'], nil )
      puts '</span></body></html>'
      exit
    end
  end
  # 一致しなければ通常のログインフォーム表示
  html_init( nil)
  html_head( nil, 0, nil )
  render_top_login( l )
  render_login_form( nil, l )
  html_foot()
end
