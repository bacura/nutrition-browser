#!/usr/bin/env ruby
#encoding: utf-8
#Nutrition browser 2020 health_sync 0.2.0 (2026/06/21)

#==============================================================================
# LIBRARY
#==============================================================================
require 'net/http'
require 'uri'
require 'date'
require './soul'
require './brain'

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )
koyomiex = $KOYOMI_PATH + "/koyomiex.cgi"


#==============================================================================
# DEFINITION
#==============================================================================
# Language pack
def language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    error:        "エラー:",
    error_auth:     "認証エラー:",
    error_reflesh:  "リフレッシュ失敗:",
    error_kex: "こよみ拡張に同期対象の項目（歩数・活動量・体重・体脂肪率）が設定されていません",
    error_api:  "Google Health APIが未認証です。設定から認証してください",
    error_client: "client_idまたはclient_secretが取得できませんでした",
    period: "取得範囲:",
    steps: "歩数",
    weight_fat: "体重・体脂肪率（kg・%）",
    activity: "活動量",
    import: "日分を取り込みました",
    health:  "<img src='bootstrap-dist/icons/heart-pulse.svg' style='height:2em; width:2em;'> Google Health import",
    reload:  "<img src='bootstrap-dist/icons/arrow-counterclockwise.svg' style='height:2em; width:2em;'>拡張こよみを更新",
  }

  return l[language]
end


def load_health_config( dbr, user )
  res = dbr.query( "SELECT result FROM #{$TBR} WHERE base='google_health' AND token='private' AND user=?", false, [user.name] )&.first
  return nil if res.nil? || res['result'].to_s.empty?
  begin
    JSON.parse( res['result'] )
  rescue JSON::ParserError
    nil
  end
end

def save_health_config( dbr, user, token_data )
  dbr.query( "UPDATE #{$TBR} SET result=? WHERE base='google_health' AND token='private' AND user=?", true, [JSON.generate( token_data ), user.name] )
end

def refresh_token!( dbr, user, health )
  uri = URI.parse( 'https://oauth2.googleapis.com/token' )
  req = Net::HTTP::Post.new( uri )
  req['Content-Type'] = 'application/x-www-form-urlencoded'
  req.set_form_data(
    grant_type:    'refresh_token',
    refresh_token: health['refresh_token'],
    client_id:     health['client_id'],
    client_secret: health['client_secret']
  )
  res       = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  new_token = JSON.parse( res.body )
  raise "#{l[:error_reflesh]} #{res.body}" if new_token['access_token'].nil?

  new_token['refresh_token'] ||= health['refresh_token']
  new_token['client_id']     = health['client_id']
  new_token['client_secret'] = health['client_secret']

  save_health_config( dbr, user, new_token )
  new_token
end

def api_post( dbr, path, body, user, health )
  uri = URI.parse( "https://health.googleapis.com#{path}" )
  req = Net::HTTP::Post.new( uri )
  req['Authorization'] = "Bearer #{health['access_token']}"
  req['Content-Type']  = 'application/json'
  req.body = JSON.generate( body )

  res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  if res.code == '401'
    health = refresh_token!( dbr, user, health )
    req['Authorization'] = "Bearer #{health['access_token']}"
    res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  end
  JSON.parse( res.body )
end

def api_get( dbr, path, user, health )
  uri = URI.parse( "https://health.googleapis.com#{path}" )
  req = Net::HTTP::Get.new( uri )
  req['Authorization'] = "Bearer #{health['access_token']}"
  req['Accept']        = 'application/json'

  res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  if res.code == '401'
    health = refresh_token!( dbr, user, health )
    req['Authorization'] = "Bearer #{health['access_token']}"
    res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  end
  JSON.parse( res.body )
end

def date_range_body( from_date, to_date )
  {
    range: {
      start: {
        date: { year: from_date.year, month: from_date.month, day: from_date.day },
        time: { hours: 0, minutes: 0, seconds: 0, nanos: 0 }
      },
      end: {
        date: { year: to_date.year, month: to_date.month, day: to_date.day },
        time: { hours: 23, minutes: 59, seconds: 59, nanos: 0 }
      }
    },
    windowSizeDays: 1
  }
end

def fetch_rollup_paged( dbr, path, from_date, to_date, max_days, user, health )
  all_points = []
  cursor = from_date
  while cursor <= to_date
    chunk_end = [cursor + max_days - 1, to_date].min
    body = date_range_body( cursor, chunk_end )
    data = api_post( dbr, path, body, user, health )
    points = data['rollupDataPoints'] || []
    all_points.concat( points )
    cursor = chunk_end + 1
  end
  all_points
end

def upsert_cell( db, date, key, value )
  res = db.query( "SELECT cell FROM #{$TB_KOYOMIEX} WHERE user=? AND date=?", false, [db.user.name, date] )&.first
  cells = {}
  if res && !res['cell'].to_s.empty?
    begin
      cells = JSON.parse( res['cell'] )
    rescue JSON::ParserError
      cells = {}
    end
  end
  cells[key] = value
  cell_ = JSON.generate( cells )
  if res
    db.query( "UPDATE #{$TB_KOYOMIEX} SET cell=? WHERE user=? AND date=?", true, [cell_, db.user.name, date] )
  else
    db.query( "INSERT INTO #{$TB_KOYOMIEX} SET cell=?, user=?, date=?", true, [cell_, db.user.name, date] )
  end
end

def civil_date_str( point )
  d = point['civilStartTime']['date']
  "%04d-%02d-%02d" % [d['year'], d['month'], d['day']]
end

def sample_date_str( point, type_key )
  d = point[type_key]['sampleTime']['civilTime']['date']
  "%04d-%02d-%02d" % [d['year'], d['month'], d['day']]
end

#==============================================================================
# MAIN
#==============================================================================
html_init( nil )

user = User.new( @cgi )
l = language_pack( user.language )
db   = Db.new( user, false, false )
dbr  = Dbr.new( user, false, false )

puts l[:health]
puts "<hr>"

if user.status < 1
  puts l[:error_auth]
  exit
end

# configからkoyomi設定を読み込む
kexu = {}
kexa = {}
res = db.query( "SELECT koyomi FROM #{$TB_CFG} WHERE user=?", false, [user.name] )&.first
if res && !res['koyomi'].to_s.empty?
  begin
    koyomi = JSON.parse( res['koyomi'] )
    kexu   = koyomi['kexu'] || {}
    kexa   = koyomi['kexa'] || {}
  rescue JSON::ParserError
    kexu = {}
  end
end

steps_key   = kexa['歩数']     == '1' ? '歩数'     : nil
calorie_key = kexa['活動量']   == '1' ? '活動量'   : nil
weight_key  = kexa['体重']     == '1' ? '体重'     : nil
fat_key     = kexa['体脂肪率'] == '1' ? '体脂肪率' : nil

if steps_key.nil? && calorie_key.nil? && weight_key.nil? && fat_key.nil?
  puts l[:error_kex]
  exit
end

health = load_health_config( dbr, user )
if health.nil? || health['access_token'].nil?
  puts l[:error_api]
  exit
end

# 取得範囲（常に直近1ヶ月）
today     = Date.today
from_date = today << 1
to_date   = today
from_str  = from_date.strftime( '%Y-%m-%d' )
to_str    = to_date.strftime( '%Y-%m-%d' )
puts "#{l[:period]} #{from_str} ～ #{to_str}<br>"

begin
  # 歩数（90日制限）
  if steps_key
    list = fetch_rollup_paged( dbr,
      '/v4/users/me/dataTypes/steps/dataPoints:dailyRollUp',
      from_date, to_date, 90, user, health
    )
    list.each do |d|
      date_str = civil_date_str( d )
      next if date_str < from_str || date_str > to_str
      upsert_cell( db, date_str, steps_key, d['steps']['countSum'].to_s )
    end
    puts "#{l[:steps]}（#{kexu[steps_key]}）#{list.size}#{l[:import]}<br>"
  end

  # 活動エネルギー（14日制限）
  if calorie_key
    list = fetch_rollup_paged( dbr,
      '/v4/users/me/dataTypes/total-calories/dataPoints:dailyRollUp',
      from_date, to_date, 14, user, health
    )
    list.each do |d|
      date_str = civil_date_str( d )
      next if date_str < from_str || date_str > to_str
      kcal = d['totalCalories']['kcalSum'].to_f.round
      upsert_cell( db, date_str, calorie_key, kcal.to_s )
    end
    puts "#{l[:activity]}（#{kexu[calorie_key]}）#{list.size}#{l[:import]}<br>"
  end

  # 体重・体脂肪率（同日に両方揃っているデータのみ採用）
  if weight_key || fat_key
    weight_data = {}
    fat_data    = {}

    if weight_key
      data = api_get( dbr, "/v4/users/me/dataTypes/weight/dataPoints?filter=weight.sample_time.civil_time%20>%3D%20%22#{from_str}%22%20AND%20weight.sample_time.civil_time%20%3C%20%22#{to_date + 1}%22", user, health )
      ( data['dataPoints'] || [] ).each do |d|
        date_str = sample_date_str( d, 'weight' )
        next if date_str < from_str || date_str > to_str
        weight_data[date_str] = ( d['weight']['weightGrams'].to_f / 1000.0 ).round( 1 )
      end
    end

    if fat_key
      data = api_get( dbr, "/v4/users/me/dataTypes/body-fat/dataPoints?filter=body_fat.sample_time.civil_time%20>%3D%20%22#{from_str}%22%20AND%20body_fat.sample_time.civil_time%20%3C%20%22#{to_date + 1}%22", user, health )
      ( data['dataPoints'] || [] ).each do |d|
        date_str = sample_date_str( d, 'bodyFat' )
        next if date_str < from_str || date_str > to_str
        fat_data[date_str] = d['bodyFat']['percentage'].to_f.round( 1 )
      end
    end

    valid_dates = weight_data.keys & fat_data.keys
    valid_dates.each do |date_str|
      upsert_cell( db, date_str, weight_key, weight_data[date_str].to_s ) if weight_key
      upsert_cell( db, date_str, fat_key,    fat_data[date_str].to_s    ) if fat_key
    end
    puts "#{l[:weight_fat]} #{valid_dates.size}#{l[:import]}<br>"
  end

  puts "<br>"
  puts "<div align='center'>"
  puts "<button type='button' class='btn btn-outline-info btn-sm nav_button' onclick='realoadKEX()'>#{l[:reload]}</button>"
  puts "</div>"

rescue => e
  puts "#{l[:error]} #{CGI.escapeHTML( e.message )}<br>"
  puts e.backtrace.first( 3 ).map { |b| CGI.escapeHTML( b ) }.join( '<br>' )
end
