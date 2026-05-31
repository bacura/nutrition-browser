#!/usr/bin/env ruby
#encoding: utf-8
#Nutrition browser 2020 fitbit_sync 0.1.0 (2026/05/17)

#==============================================================================
# LIBRARY
#==============================================================================
require 'net/http'
require 'uri'
require 'base64'
require './soul'

#==============================================================================
# STATIC
#==============================================================================
#client_id     = '23VBLT'
#client_secret = '31994097efefd31ff3b68dd06afcb6fe'

#==============================================================================
# DEFINITION
#==============================================================================

def load_token( user )
  cfg = Config.new( user, 'fitbit' )
  token = cfg.val
  return nil if token.nil? || token.empty?
  token
end

def save_token( user, token_data )
  cfg = Config.new( user, 'fitbit' )
  cfg.set_hash( token_data )
  cfg.update
end

def refresh_token!( user, token_data, client_id, client_secret )
  uri = URI.parse( 'https://api.fitbit.com/oauth2/token' )
  req = Net::HTTP::Post.new( uri )
  req['Authorization'] = "Basic #{Base64.strict_encode64( "#{client_id}:#{client_secret}" )}"
  req['Content-Type']  = 'application/x-www-form-urlencoded'
  req.set_form_data(
    grant_type:    'refresh_token',
    refresh_token: token_data['refresh_token']
  )
  res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  new_token = JSON.parse( res.body )
  raise "リフレッシュ失敗: #{res.body}" if new_token['access_token'].nil?
  save_token( user, new_token )
  new_token
end

def api_get( path, user, token_data, client_id, client_secret )
  uri = URI.parse( "https://api.fitbit.com#{path}" )
  req = Net::HTTP::Get.new( uri )
  req['Authorization'] = "Bearer #{token_data['access_token']}"
  res = Net::HTTP.start( uri.host, uri.port, use_ssl: true ) { |http| http.request( req ) }
  if res.code == '401'
    token_data = refresh_token!(user, token_data, client_id, client_secret)
    req['Authorization'] = "Bearer #{token_data['access_token']}"
    res = Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |http| http.request( req ) }
  end
  JSON.parse( res.body )
end

def upsert_cell( db, date, key, value )
  res = db.query("SELECT cell FROM #{$TB_KOYOMIEX} WHERE user=? AND date=?", false, [db.user.name, date] )&.first
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

# koyomiexから取得期間内の体重データを読み込む
# 戻り値: { '2026-01-01' => 61.5, ... } 日付文字列をキーとしたHash
def load_koyomiex_weight( db, weight_key, from_str, to_str )
  weights = {}
  return weights if weight_key.nil?
  res = db.query( "SELECT date, cell FROM #{$TB_KOYOMIEX} WHERE user=? AND date BETWEEN ? AND ? ORDER BY date", false, [db.user.name, from_str, to_str] )
  res.each do |row|
    next if row['cell'].to_s.empty?
    begin
      cells = JSON.parse( row['cell'] )
      w = cells[weight_key].to_f
      weights[row['date'].to_s] = w if w > 0
    rescue JSON::ParserError
      next
    end
  end
  weights
end

# 指定日以前で最も直近の体重を返す
def nearest_weight( weights, date_str )
  candidate = weights.keys.sort.select { |d| d <= date_str }.last
  candidate ? weights[candidate] : nil
end

#==============================================================================
# MAIN
#==============================================================================
#puts "Content-type: text/html; charset=utf-8\n\n"
html_init( nil )
user = User.new( @cgi )
db = Db.new( user, @debug, false )

if user.status < 1
  puts "認証エラー"
  exit
end

# configからkoyomi設定を読み込む
kexu       = {}
start_date = nil
res = db.query( "SELECT koyomi, fitbit FROM #{$TB_CFG} WHERE user=?",false, [user.name] )&.first
if res && !res['koyomi'].to_s.empty?
  begin
    koyomi     = JSON.parse( res['koyomi'] )
    kexu       = koyomi['kexu'] || {}
    start_date = koyomi['start'].to_s unless koyomi['start'].to_s.empty?
  rescue JSON::ParserError
    kexu = {}
  end
end

# configからfitbit設定を読み込む
if res && !res['fitbit'].to_s.empty?
  begin
    fitbit     = JSON.parse( res['fitbit'] )
    client_id  = fitbit['client_id'] || {}
    client_secret = fitbit['client_secret'] || {}

  rescue JSON::ParserError
    client_id = nil
    client_secret = nil
  end
end

# キー探索
steps_key   = kexu.find { |k, v| v == '歩' }&.first
calorie_key = kexu.key?('活動量') ? '活動量' : nil
weight_key  = kexu.find { |k, v| v == 'kg' }&.first

if steps_key.nil? && calorie_key.nil?
  puts "こよみ拡張に歩数（単位：歩）または活動量が設定されていません。"
  exit
end

# Fitbitトークン読み込み
token_data = load_token( user )
if token_data.nil?
  puts "Fitbitが未認証です。fitbit_auth.cgiで認証してください。"
  exit
end

# 取得範囲の計算
today     = Date.today
api_limit = today - 1095
begin
  from_date = Date.parse(start_date)
rescue
  from_date = today << 1
end
from_date = api_limit if from_date < api_limit
to_date   = today

from_str = from_date.strftime( '%Y-%m-%d' )
to_str   = to_date.strftime( '%Y-%m-%d' )

puts "取得範囲: #{from_str} ～ #{to_str}<br>"

begin
  # 歩数の同期
  if steps_key
    data = api_get( "/1/user/-/activities/steps/date/#{from_str}/#{to_str}.json", user, token_data, client_id, client_secret )
    steps_list = data['activities-steps']
    steps_list.each do |d|
      upsert_cell( db, d['dateTime'], steps_key, d['value'] )
    end
    puts "✅ 歩数（ #{steps_key} ）#{steps_list.size}日分を保存しました。<br>"
  end

  # 活動量の同期
  if calorie_key
    # FitbitからAPI経由で体重を取得（日ごと）
    fitbit_weights = {}
    w_data = api_get( "/1/user/-/body/weight/date/#{from_str}/#{to_str}.json", user, token_data, client_id, client_secret )
    w_data['body-weight'].each do |d|
      w = d['value'].to_f
      fitbit_weights[d['dateTime']] = w if w > 0
    end

    # koyomiexから体重データを読み込む
    koyomiex_weights = load_koyomiex_weight( db, weight_key, from_str, to_str )
    has_koyomiex_weight = !koyomiex_weights.empty?

    # 活動量を取得して補正
    data = api_get( "/1/user/-/activities/calories/date/#{from_str}/#{to_str}.json", user, token_data, client_id, client_secret )
    calories_list = data['activities-calories']

    calories_list.each do |d|
      date_str   = d['dateTime']
      kcal       = d['value'].to_f
      fitbit_w   = fitbit_weights[date_str] || nearest_weight( fitbit_weights, date_str )

      if has_koyomiex_weight && fitbit_w && fitbit_w > 0
        # 同日または直近のkoyomiex体重で補正
        kex_w = koyomiex_weights[date_str] || nearest_weight( koyomiex_weights, date_str )
        kcal  = ( kcal * kex_w / fitbit_w ).round if kex_w && kex_w > 0
      end

      upsert_cell( db, date_str, calorie_key, kcal.to_s )
    end

    msg = has_koyomiex_weight ? '体重補正あり' : '体重データなし・補正なし'
    puts "✅ 活動量（ #{msg} ）#{calories_list.size}日分を保存しました。<br>"
    puts "拡張こよみを再読み込みしてください。"
  end

rescue => e
  puts "エラー: #{CGI.escapeHTML( e.message )}"
end
