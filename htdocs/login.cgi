#! /usr/bin/ruby
# coding: utf-8
# Nutrition browser 2020 login 0.1.3 (2026/01/09)

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
    empty:    "[空き地]"
  }

  return l[language]
end

def render_html( content )
  puts content
end

def render_login_form( msg, l )
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
end

def update_user_data( db, user_data, cgi )
  status = user_data['status'].to_i
  uid = user_data['cookie'] || SecureRandom.hex( 16 )
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
  login_mv = get_data['login_mv']
  res = db.query( "SELECT * FROM #{$TB_USER} WHERE user=?", false, [login_mv] )&.first
  handle_login_mv( db, res ) if res
end

def handle_login_mv( db, login_data )
  cookie = if login_data['mom'].to_s.empty?
    "Set-Cookie: NAME=#{login_data['user']}\nSet-Cookie: #{$COOKIE_UID}=#{login_data['cookie']}\n"
  else
    handle_family_cookie( db, login_data )
  end
  db.query( "UPDATE #{$TB_USER} SET cookie_m=NULL WHERE user=?", true, [db.user.name] )
  html_init( cookie )
  html_head( 'refresh', login_data['status'], nil )
  puts '</span></body></html>'
end

def handle_family_cookie( db, login_data )
  parent_res = db.query( "SELECT * FROM #{$TB_USER} WHERE user=?", false, [login_data['mom']] )&.first
  return unless parent_res

  uid = login_data['cookie']
#  uid = SecureRandom.hex( 16 )

  parent_cookie = parent_res.first['cookie']
  db.query( "UPDATE #{$TB_USER} SET cookie=?, cookie_m=? WHERE user=?", true, [uid, parent_cookie, login_data['user']] )
  "Set-Cookie: NAME=#{login_data['user']}\nSet-Cookie: #{$COOKIE_UID}=#{uid}\n"
end

#==============================================================================
# MAIN
#==============================================================================
text_init() if @debug

get_data = get_data()
user = User.new( @cgi )
l = language_pack( user.language )
if l.nil?
  puts 'U(x_x)L'
  exit
end
db = Db.new( user, false, true )


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
    html_init( nil )
    html_head( nil, 0, nil )
    render_top_login( l )
    render_login_form( nil, l )
    html_foot()
end
