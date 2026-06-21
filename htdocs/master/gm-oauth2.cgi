#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 GM OAuth2.0 for Google Health 0.0.0 (2026/06/20)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'
require '../brain'

#==============================================================================
#DEFINITION
#==============================================================================
# Language pack
def language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    title:    "OAuth 2.0 for Google Health API",
    auth_id:  "OAuth 2.0 Client ID",
    secret:   "Client Secret",
    save:     "保存"
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
dbr = Dbr.new( user, @debug, false )

command = @cgi['command']
client_id = @cgi['client_id'].to_s
client_secret = @cgi['client_secret'].to_s

if user.status < 9
  puts 'GM error.'
  exit
end

if command == 'save'
  res = dbr.qq( "SELECT result FROM #{$TBR} WHERE base='OAuth2_GH' and token='client_id' and user='#{$GM}';" )&.first
  if res
    dbr.query( "UPDATE #{$TBR} SET result=? WHERE base='OAuth2_GH' and token='client_id' and user=?;", true, [client_id, user.name] )
  else
    dbr.query( "INSERT INTO #{$TBR} SET result=?, base='OAuth2_GH', token='client_id', user=?;", true, [client_id, user.name] )
  end

  res = dbr.qq( "SELECT result FROM #{$TBR} WHERE base='OAuth2_GH' and token='client_secret' and user='#{$GM}';" )&.first
  if res
    dbr.query( "UPDATE #{$TBR} SET result=? WHERE base='OAuth2_GH' and token='client_secret' and user=?;", true, [client_secret, user.name] )
  else
    dbr.query( "INSERT INTO #{$TBR} SET result=?, base='OAuth2_GH', token='client_secret', user=?;", true, [client_secret, user.name] )
  end
else
  res = dbr.qq( "SELECT result FROM #{$TBR} WHERE base='OAuth2_GH' and token='client_id' and user='#{$GM}';" )&.first
  client_id = res['result'] if res

  res = dbr.qq( "SELECT result FROM #{$TBR} WHERE base='OAuth2_GH' and token='client_secret' and user='#{$GM}';" )&.first
  client_secret = res['result'] if res
end


html = <<~HTML
  <div class="container">
    <div class='row'>
        <div class='col'><h5>#{l[:title]}</h5></div>
    </div>
    <br>

    <div class='row'>
      <div class='col-2'>#{l[:auth_id]}</div>
      <div class='col-10'><input type="text" id="client_id" class="form-control login_input" value="#{client_id}"></div>
    </div>
    <div class='row'>
      <div class='col-2'>#{l[:secret]}</div>
      <div class='col-10'><input type="text" id="client_secret" class="form-control login_input" value="#{client_secret}"></div>
    </div>
    <br>

    <div class='row'>
        <button type="button" class="btn btn-outline-primary btn-sm" onclick="OAuthSave()">#{l[:save]}</button>
    </div>
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

var OAuthSave = () => {
  const client_id     = document.getElementById( 'client_id' ).value;
  const client_secret = document.getElementById( 'client_secret' ).value;
  if( !client_id || !client_secret ){
    alert( 'Client IDとClient Secretを入力してください' );
    return;
  }

  postLayer( mp + '#{myself}', 'save', true, 'L1', { client_id, client_secret });
};
</script>

JS
  puts js
end

puts '(^q^)' if @debug
