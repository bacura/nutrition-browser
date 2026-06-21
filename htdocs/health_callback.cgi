#!/usr/bin/env ruby
#encoding: utf-8
#Nutrition browser 2020 health_callback 0.2.0 (2026/06/21)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require './brain'
require 'net/http'
require 'uri'
require 'base64'

#==============================================================================
# DEFINITION
#==============================================================================
# Language pack
def language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    error:        "エラー:",
    error_auth:   "認証エラー:",
    error_nc:     "認証コードがありません",
    error_client: "client_idまたはclient_secretが取得できませんでした",
    error_token:  "トークン取得失敗",
    error_client: "client_idまたはclient_secretが取得できませんでした",
    finish:       "<img src='bootstrap-dist/icons/google.svg' style='height:2em; width:2em;'>",
    save:       "<p>Google Healthと連携しました<br>ウインドウを閉じても大丈夫です"
  }

  return l[language]
end


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
l = language_pack( user.language )
dbr = Dbr.new( user, @debug, false )


# エラーチェック
if @cgi['error'] != ''
  puts "#{l[:error_auth]} #{CGI.escapeHTML( @cgi['error'] )}"
  exit
end

code  = @cgi['code']

if code.empty?
  puts l[:error_nc]
  exit
end


res = dbr.qq( "SELECT result FROM #{$TBR} WHERE base='OAuth2_GH' and token='client_id' and user='#{$GM}';" )&.first
client_id = res['result'] if res

res = dbr.qq( "SELECT result FROM #{$TBR} WHERE base='OAuth2_GH' and token='client_secret' and user='#{$GM}';" )&.first
client_secret = res['result'] if res

if client_id.empty? || client_secret.empty?
  puts l[:error_client]
  exit
end



# 認証コード → アクセストークン交換
begin
  uri = URI.parse( 'https://oauth2.googleapis.com/token' )
  req = Net::HTTP::Post.new( uri )
  req['Content-Type'] = 'application/x-www-form-urlencoded'
  req.set_form_data(
    grant_type:    'authorization_code',
    code:          code,
    redirect_uri:  $HEALTH_REDIRECT_URI,
    client_id:     client_id,
    client_secret: client_secret
  )

  res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  token_data = JSON.parse( res.body )

  if token_data['access_token'].nil?
    puts "#{l[:error_token]}<pre>#{CGI.escapeHTML( res.body )}</pre>"
    exit
  end

  # client_id・client_secretとトークンをDBに保存
  health_ = JSON.generate({
    'client_id'     => client_id,
    'client_secret' => client_secret,
    'access_token'  => token_data['access_token'],
    'refresh_token' => token_data['refresh_token'],
    'expires_in'    => token_data['expires_in'],
    'token_type'    => token_data['token_type'],
    'scope'         => token_data['scope']
  })

  res = dbr.query( "SELECT result FROM #{$TBR} WHERE base='google_health' AND token='private' AND user=?", false, [user.name] )&.first
  if res
    dbr.query( "UPDATE #{$TBR} SET result=? WHERE base='google_health' AND token='private' AND user=?", true, [health_, user.name] )
  else
    dbr.query( "INSERT #{$TBR} SET result=?, base='google_health', token='private', user=?", true, [health_, user.name] )
  end

  puts <<~"HTML"
    #{l[:finish]}
    <hr>
    #{l[:save]}
  HTML

rescue => e
  puts "#{l[:error]}<pre>#{CGI.escapeHTML( e.message )}</pre>"
end
