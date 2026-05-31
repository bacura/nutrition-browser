#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 fitbit_allback test 0.0.0 (2026/05/24)

#==============================================================================
#LIBRARY
#==============================================================================
require 'net/http'
require 'uri'
require 'base64'
require './soul'

#==============================================================================
#STATIC
#==============================================================================


#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================
user = User.new( @cgi )
db = Db.new( user, @debug, false )

# エラーチェック
if @cgi['error'] != ''
  @cgi.out( 'type' => 'text/html', 'charset' => 'utf-8' ){
    "<html><body><h2>認証エラー: #{CGI.escapeHTML( @cgi['error'] )}</h2></body></html>"
  }
  exit
end

code = @cgi['code']
if code.empty?
  @cgi.out( 'type' => 'text/html', 'charset' => 'utf-8' ){
    "<html><body><h2>認証コードがありません</h2></body></html>"
  }
  exit
end


res = db.query( "SELECT fitbit FROM #{$TB_CFG} WHERE user=?", false, [user.name] )&.first
unless res['fitbit'].to_s.empty?
  begin
    fitbit = JSON.parse( res['fitbit'] )
  rescue JSON::ParserError => e
    puts "J(x_x)pE: #{e.message}<br>"
    exit
  end     

  client_id = fitbit['client_id'].to_s
  client_secret = fitbit['client_secret'].to_s
end


begin
  uri = URI.parse( 'https://api.fitbit.com/oauth2/token' )
  req = Net::HTTP::Post.new( uri )
  req['Authorization'] = "Basic #{Base64.strict_encode64( "#{client_id}:#{client_secret}" )}"
  req['Content-Type']  = 'application/x-www-form-urlencoded'
  req.set_form_data(
    grant_type:   'authorization_code',
    code:         code,
    redirect_uri: $FITBIT_REDIRECT_URI
  )

  res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request(req) }
  token_data = JSON.parse( res.body )

  if token_data['access_token'].nil?
    @cgi.out( 'type' => 'text/html', 'charset' => 'utf-8' ) {
      "<html><body><h2>トークン取得失敗</h2><pre>#{CGI.escapeHTML( res.body )}</pre></body></html>"
    }
    exit
  end

  # DBに保存
  cfg = Config.new( user, 'fitbit' )
  cfg.set_hash(token_data)
  cfg.update

  @cgi.out( 'type' => 'text/html', 'charset' => 'utf-8' ) {
    <<~HTML
      <html><body>
        <h2>認証完了！</h2>
        <p>トークンをDBに保存しました。ページを閉じても大丈夫です。</p>
      </body></html>
    HTML
  }

rescue => e
  @cgi.out('type' => 'text/html', 'charset' => 'utf-8') {
    "<html><body><h2>エラー</h2><pre>#{CGI.escapeHTML( e.message )}</pre></body></html>"
  }
end
