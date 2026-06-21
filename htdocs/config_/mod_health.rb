# Nutrition browser 2020 Config module for Google Health API 0.3.0 (2026/06/21)
#encoding: utf-8

@debug = false
require './brain'

def config_module( cgi, db )
  module_js( cgi['mod'] )
  l = module_lp( db.user.language )
  dbr = Dbr.new( db.user, @debug, false )

  client_id = ''
  res = dbr.qq( "SELECT result FROM #{$TBR} WHERE base='OAuth2_GH' and token='client_id' and user='#{$GM}';" )&.first
  client_id = res['result'] if res

  client_secret = ''
  res = dbr.qq( "SELECT result FROM #{$TBR} WHERE base='OAuth2_GH' and token='client_secret' and user='#{$GM}';" )&.first
  client_secret = res['result'] if res
  if client_id.empty? || client_secret.empty?
    puts l[:unable]
    exit
  end

  # Cancel
  dbr.query( "DELETE FROM #{$TBR} WHERE base='google_health' AND token='private' AND user=?", false, [dbr.user.name] ) if cgi['step'] == 'cancel'

  res = dbr.query( "SELECT result FROM #{$TBR} WHERE base='google_health' AND token='private' AND user=?", false, [dbr.user.name] )&.first
  if res
    button = "<button type='button' class='btn btn-warning btn-sm' onclick='health_auth_cancel( \"cancel\" )'>#{l[:auth2_cancel]}</button>"
  else
    button = "<button type='button' class='btn btn-primary btn-sm' onclick='health_auth( \"#{client_id}\", \"#{client_secret}\" )'>#{l[:auth2_bind]}</button>"
  end

  html = <<~HTML
      <div class='row'>#{button}</div>
  HTML

  return html
end

def module_js( mod )
  scopes = [
    'https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly',
    'https://www.googleapis.com/auth/googlehealth.health_metrics_and_measurements.readonly',
    'https://www.googleapis.com/auth/googlehealth.profile.readonly',
    'https://www.googleapis.com/auth/googlehealth.sleep.readonly'
  ].join(' ')

  js = <<-"JS"
<script type='text/javascript'>
var health_auth = ( client_id, client_secret ) => {
  if( !client_id || !client_secret ){
    alert( 'OAuth2 Error No id/secret' );
    return;
  }
  const redirect = encodeURIComponent( '#{$HEALTH_REDIRECT_URI}' );
  const scope    = encodeURIComponent( '#{scopes}' );
  const auth_url = 'https://accounts.google.com/o/oauth2/auth'
    + '?response_type=code'
    + '&client_id=' + encodeURIComponent( client_id )
    + '&redirect_uri=' + redirect
    + '&scope=' + scope
    + '&access_type=offline'
    + '&prompt=consent';
  window.open( auth_url, 'health' );
};


var health_auth_cancel = ( step ) => {
  postLayer( 'config.cgi', 'dummy', true, 'L1', { mod:'#{mod}', step });
}


</script>
JS
  puts js
end

def module_lp( language )
  l = Hash.new
  l['ja'] = {
    'mod_name' => "Google Health連携",
    auth2_bind:     "Google Healthと連携する",
    auth2_cancel:     "Google Healthとの連携を解除する",
    unable:    "現在、Google Healthと連携は出来ません"
  }
  return l[language]
end
