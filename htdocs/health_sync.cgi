#!/usr/bin/env ruby
#encoding: utf-8
#Nutrition browser 2020 health_sync 0.3.1 (2026/07/25)

#==============================================================================
# LIBRARY
#==============================================================================
require 'net/http'
require 'uri'
require 'date'
require 'time'
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
    error_kex: "こよみ拡張に同期対象の項目（歩数・活動量・体重・体脂肪率・睡眠）が設定されていません",
    error_api:  "Google Health APIが未認証です。設定から認証してください",
    error_client: "client_idまたはclient_secretが取得できませんでした",
    period: "取得範囲:",
    steps: "歩数",
    weight_fat: "体重・体脂肪率（kg・%）",
    activity: "活動量",
    sleep: "睡眠時間",
    import: "日分を取り込みました",
    health:  "<img src='bootstrap-dist/icons/heart-pulse.svg' style='height:2em; width:2em;'> Google Health import",
    close:  "閉じて更新",
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

def refresh_token!( dbr, user, health, l )
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

def api_post( dbr, path, body, user, health, l )
  uri = URI.parse( "https://health.googleapis.com#{path}" )
  req = Net::HTTP::Post.new( uri )
  req['Authorization'] = "Bearer #{health['access_token']}"
  req['Content-Type']  = 'application/json'
  req.body = JSON.generate( body )

  res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  if res.code == '401'
    health = refresh_token!( dbr, user, health, l )
    req['Authorization'] = "Bearer #{health['access_token']}"
    res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  end
  JSON.parse( res.body )
end

def api_get( dbr, l, path, user, health )
  uri = URI.parse( "https://health.googleapis.com#{path}" )
  req = Net::HTTP::Get.new( uri )
  req['Authorization'] = "Bearer #{health['access_token']}"
  req['Accept']        = 'application/json'

  res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  if res.code == '401'
    health = refresh_token!( dbr, user, health, l )
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

def fetch_rollup_paged( dbr, l, path, from_date, to_date, max_days, user, health )
  all_points = []
  cursor = from_date
  while cursor <= to_date
    chunk_end = [cursor + max_days - 1, to_date].min
    body = date_range_body( cursor, chunk_end )
    data = api_post( dbr, path, body, user, health, l )
    points = data['rollupDataPoints'] || []
    all_points.concat( points )
    cursor = chunk_end + 1
  end
  all_points
end

def fetch_reconcile_paged( dbr, l, path, filter, user, health )
  all_points = []
  page_token = nil

  loop do
    query = "?filter=#{CGI.escape( filter )}&pageSize=1000"
    query += "&pageToken=#{CGI.escape( page_token )}" if page_token
    data = api_get( dbr, l, "#{path}:reconcile#{query}", user, health )
    all_points.concat( data['dataPoints'] || [] )
    page_token = data['nextPageToken']
    break if page_token.nil? || page_token.to_s.empty?
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

def local_date_from_utc( iso_time_str, utc_offset_str )
  t = Time.parse( iso_time_str )
  offset_sec = utc_offset_str.to_s.sub( 's', '' ).to_i
  ( t + offset_sec ).strftime( '%Y-%m-%d' )
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
sleep_key   = kexa['睡眠']     == '1' ? '睡眠'     : nil

if steps_key.nil? && calorie_key.nil? && weight_key.nil? && fat_key.nil? && sleep_key.nil?
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
    list = fetch_rollup_paged( dbr, l,
      '/v4/users/me/dataTypes/steps/dataPoints:dailyRollUp',
      from_date, to_date, 90, user, health
    )
    imported = 0
    list.each do |d|
      count = d.dig( 'steps', 'countSum' )
      next if count.nil?  # 値が無いレコードは取り込まない（nil.to_sで空文字が入るのを防ぐ）

      date_str = civil_date_str( d )
      next if date_str < from_str || date_str > to_str
      upsert_cell( db, date_str, steps_key, count.to_s )
      imported += 1
    end
    puts "#{l[:steps]}（#{kexu[steps_key]}）#{imported}#{l[:import]}<br>"
  end

  # 活動エネルギー（14日制限）
  if calorie_key
    list = fetch_rollup_paged( dbr, l,
      '/v4/users/me/dataTypes/total-calories/dataPoints:dailyRollUp',
      from_date, to_date, 14, user, health
    )
    imported = 0
    list.each do |d|
      kcal_sum = d.dig( 'totalCalories', 'kcalSum' )
      next if kcal_sum.nil?  # 値が無いレコードは取り込まない（nil.to_fで0が入るのを防ぐ）

      date_str = civil_date_str( d )
      next if date_str < from_str || date_str > to_str
      kcal = kcal_sum.to_f.round
      upsert_cell( db, date_str, calorie_key, kcal.to_s )
      imported += 1
    end
    puts "#{l[:activity]}（#{kexu[calorie_key]}）#{imported}#{l[:import]}<br>"
  end

  # 体重・体脂肪率（同日に両方揃っているデータのみ採用）
  if weight_key || fat_key
    weight_data = {}
    fat_data    = {}

    if weight_key
      data = api_get( dbr, l, "/v4/users/me/dataTypes/weight/dataPoints?filter=weight.sample_time.civil_time%20>%3D%20%22#{from_str}%22%20AND%20weight.sample_time.civil_time%20%3C%20%22#{to_date + 1}%22", user, health )
      ( data['dataPoints'] || [] ).each do |d|
        weight_grams = d.dig( 'weight', 'weightGrams' )
        next if weight_grams.nil?  # 値が無いレコードは取り込まない（nil.to_fで0kgが入るのを防ぐ）

        date_str = sample_date_str( d, 'weight' )
        next if date_str < from_str || date_str > to_str
        weight_data[date_str] = ( weight_grams.to_f / 1000.0 ).round( 1 )
      end
    end

    if fat_key
      data = api_get( dbr, l, "/v4/users/me/dataTypes/body-fat/dataPoints?filter=body_fat.sample_time.civil_time%20>%3D%20%22#{from_str}%22%20AND%20body_fat.sample_time.civil_time%20%3C%20%22#{to_date + 1}%22", user, health )
      ( data['dataPoints'] || [] ).each do |d|
        percentage = d.dig( 'bodyFat', 'percentage' )
        next if percentage.nil?  # 値が無いレコードは取り込まない（nil.to_fで0%が入るのを防ぐ）

        date_str = sample_date_str( d, 'bodyFat' )
        next if date_str < from_str || date_str > to_str
        fat_data[date_str] = percentage.to_f.round( 1 )
      end
    end

    valid_dates = weight_data.keys & fat_data.keys
    valid_dates.each do |date_str|
      upsert_cell( db, date_str, weight_key, weight_data[date_str].to_s ) if weight_key
      upsert_cell( db, date_str, fat_key,    fat_data[date_str].to_s    ) if fat_key
    end
    puts "#{l[:weight_fat]} #{valid_dates.size}#{l[:import]}<br>"
  end

# 睡眠時間（reconcileで取得し、起床日(endTime+utcOffsetのローカル日付)に帰属させる。昼寝は除外）
  if sleep_key
    filter = "sleep.interval.civil_end_time >= \"#{from_str}\" AND sleep.interval.civil_end_time < \"#{(to_date + 1)}\""
    list = fetch_reconcile_paged( dbr, l,
      '/v4/users/me/dataTypes/sleep/dataPoints',
      filter, user, health
    )

    sleep_minutes = {}
    list.each do |d|
      s = d['sleep']
      next if s.nil?
      next if s.dig( 'metadata', 'nap' )  # 昼寝は除外

      interval = s['interval']
      next if interval.nil? || interval['endTime'].nil?

      date_str = local_date_from_utc( interval['endTime'], interval['endUtcOffset'] )
      next if date_str < from_str || date_str > to_str

      minutes = s.dig( 'summary', 'minutesAsleep' )
      next if minutes.nil?

      sleep_minutes[date_str] = ( sleep_minutes[date_str] || 0 ) + minutes.to_i
    end

    sleep_minutes.each do |date_str, minutes|
      hours = ( minutes.to_f / 60 ).round( 1 )
      upsert_cell( db, date_str, sleep_key, hours.to_s )
    end
    puts "#{l[:sleep]}（#{kexu[sleep_key]}）#{sleep_minutes.size}#{l[:import]}<br>"
  end

  puts "<br>"
  puts "<div align='center'>"
  puts "<button type='button' class='btn btn-info btn-sm nav_button' onclick='realoadKEX()'>#{l[:close]}</button>"
  puts "</div>"

rescue => e
  puts "#{l[:error]} #{CGI.escapeHTML( e.message )}<br>"
  puts e.backtrace.first( 3 ).map { |b| CGI.escapeHTML( b ) }.join( '<br>' )
end
