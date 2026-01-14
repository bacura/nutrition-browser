#Nutrition browser 2020 soul 1.13.3 (2026/01/13)

#==============================================================================
# LIBRARY
#==============================================================================
require 'cgi'
require 'mysql2'
require 'securerandom'
require 'json'


#==============================================================================
#STATIC
#==============================================================================
$GM = 'gm'

$NBURL = 'https://bacura.jp/nb/'
$MYURL = 'https://eiyo-b.com/'

$MYSQL_HOST = 'localhost'
$MYSQL_DB = 'nb2020'
$MYSQL_DBR = 'rr2020'
$MYSQL_USER = 'user'
$MYSQL_USERR = 'userr'
$MYSQL_PW = 'password'

$TB_CFG = 'cfg'
$TB_DIC = 'dic'
$TB_EXT = 'ext'
$TB_FCT = 'fct'
$TB_FCTP = 'fctp'
$TB_FCTS = 'fcts'
$TB_FCZ = 'fcz'
$TB_HIS = 'his'
$TB_KOYOMI = 'koyomi'
$TB_KOYOMIEX = 'koyomiex'
$TB_MEAL = 'meal'
$TB_MEDIA = 'media'
$TB_MEMORY = 'memory'
$TB_MENU = 'menu'
$TB_METS = 'mets'
$TB_METST = 'metst'
$TB_MODJ = 'modj'
$TB_NOTE = 'note'
$TB_PAG = 'pag'
$TB_PALETTE = 'palette'
$TB_PARA = 'ref_para'
$TB_PRICE = 'price'
$TB_PRICEM = 'pricem'
$TB_RECIPE = 'recipe'
$TB_RECIPEI = 'recipei'
$TB_REFITS = 'ref_its'
$TB_SLOGF = 'slogf'
$TB_SLOGR = 'slogr'
$TB_SLOGM = 'slogm'
$TB_SUM = 'sum'
$TB_TAG = 'tag'
$TB_TENSEI = 'tensei'
$TB_USER = 'user'

$JQUERY = '<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>'
$BS_CSS = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">' 
$BS_JS = '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>' 

$SERVER_PATH = '/var/www'
$HTDOCS_PATH = "#{$SERVER_PATH}/htdocs"
$TMP_PATH = '/tmp'
$JS_PATH = 'js'
$CSS_PATH = 'scss'
$BOOK_PATH = 'books'
$KOYOMI_PATH = 'koyomi'

$PHOTO = 'photo_'
$SPHOTO = 'sphoto_'
$QR = 'qr_'
$PHOTO_PATH = "#{$HTDOCS_PATH}/#{$PHOTO}"
$SPHOTO_PATH = "#{$SERVER_PATH}/#{$SPHOTO}"
$QR_PATH = "#{$HTDOCS_PATH}/#{$QR}"
$SIZE_MAX = 20000000
$TN_SIZE = 400
$TNS_SIZE = 40
$PHOTO_SIZE_MAX = 2000

$TOKEN_SIZE = 64 #max 128

$COOKIE_UID = 'UID2020'

$SELECT = { true => 'SELECTED', false => '', 1 => 'SELECTED', 0 => '', '1' => 'SELECTED', '0' => ''}
$CHECK = { true => 'CHECKED', false => '', 1 => 'CHECKED', 0 => '', '1' => 'CHECKED', '0' => ''}
$DISABLE = { true => 'DISABLED', false => '', 1 => 'DISABLED', 0 => '', '1' => 'DISABLED', '0' => ''}

begin
  $DB = Mysql2::Client.new(:host => "#{$MYSQL_HOST}", :username => "#{$MYSQL_USER}", :password => "#{$MYSQL_PW}", :database => "#{$MYSQL_DB}", :encoding => "utf8" )
rescue
  begin
    $DB = Mysql2::Client.new(:host => "#{$MYSQL_HOST}", :username => "#{$MYSQL_USER}", :password => "#{$MYSQL_PW}", :encoding => "utf8" )
  rescue
    puts 'D(x_x)B'
  end
end

$DEBUG = false

#==============================================================================
# CGI & LANGAGE
#==============================================================================
@cgi = CGI.new

$LP = %w[ja en]

uname = @cgi.cookies['NAME']&.first
uid = @cgi.cookies[$COOKIE_UID]&.first
tmp_language = nil

if uname && uid
  res = $DB.prepare( "SELECT * FROM #{$TB_USER} WHERE user=? AND cookie=? AND status > 0" ).execute( uname, uid )&.first
  tmp_language = res['language'] if res
end
tmp_language = ENV['HTTP_ACCEPT_LANGUAGE']&.split(',')&.first&.split(';')&.first unless tmp_language

$DEFAULT_LP = $LP.include?( tmp_language ) ? tmp_language : $LP[0]

require "#{$SERVER_PATH}/nb2020-local-#{$DEFAULT_LP}"
#require "#{$SERVER_PATH}/nb-local-#{$DEFAULT_LP}"

#==============================================================================
#DEFINITION
#==============================================================================
#### HTML init
def html_init( cookie )
  puts "Content-type: text/html\n"
  puts "Cache-Control: no-store, no-cache, must-revalidate, max-age=0\n"
  puts "Cache-Control: post-check=0, pre-check=0, false\n"
  puts "Pragma: no-cache\n"
  puts cookie unless cookie == nil
  puts "\n"
end


#### HTML init with cache
def html_init_cache( cookie )
  puts "Content-type: text/html\n"
  puts cookie unless cookie == nil
  puts "\n"
end


#### TEXT init
def text_init
  puts "Content-type: text/text\n"
  puts "\n"
end


#### GETデータの抽出
def get_data()
  data = Hash.new
  if ENV['QUERY_STRING']
    querys = ENV['QUERY_STRING'].split( '&' )
    querys.each { |e|
      ( k, v ) = e.split( '=' )
      data[ k ] = v
    }
  end

  return data
end


#### DB process
#将来的に廃止
def mdb( query, html_opt, debug )
  puts "<span class='dbq'>[mdb]#{query}</span><br>" if debug
  begin
    db = Mysql2::Client.new(:host => "#{$HOST}", :username => "#{$USER}", :password => "#{$PW}", :database => "#{$DB}", :encoding => "utf8" )
    t = query.chop
    if /[\;\$]/ =~ t
        puts "<span class='error'>[mdb]ERROR!!</span><br>"
        exit( 9 )
    end
    res = db.query( query )
    db.close
  rescue
    if html_opt
      html_init( nil )
      html_head( nil )
    end
      puts "<span class='error'>[mdb]ERROR!!</span><br>"
  end
  return res
end


#### Adding history
def add_his( user, code )
  return if user.barrier

  his_max = 200
  res = $DB.prepare( "SELECT history FROM #{$TB_CFG} WHERE user=?" ).execute( user.name )
  if res.first
    if res.first['history'] != nil && res.first['history'] != ''
      history = JSON.parse( res.first['history'] )
      his_max = history['his_max'].to_i if history['his_max']
    end
  end
  his_max = 200 if his_max < 200 || his_max > 1000

  current_his = []
  res = $DB.prepare( "SELECT his FROM #{$TB_HIS} WHERE user=?" ).execute( user.name )
  current_his = res.first['his'].split( "\t" ) if res.first

  current_his.unshift( code )
  current_his.delete( '' )
  current_his.uniq!
  new_his = current_his.take( his_max ).join( "\t" )
  
  $DB.prepare( "UPDATE #{$TB_HIS} SET his=? WHERE user=?" ).execute( new_his, user.name )
end


#### コードの生成
def generate_code( uname, attribute )
  skip = false
  code = nil

  if attribute.to_s == '' || uname.to_s.size < 5
    puts "Code(x_x)Gen Pre"
    exit
  end

  code_sub = uname[0, 3].downcase
  10.times do
    code = "#{code_sub}-#{attribute}-#{SecureRandom.alphanumeric( 20 )}"
    query = ''
    case attribute
    when 'm'
      query = "SELECT * FROM #{$TB_MENU} WHERE code=?"
    when 'n'
      query = "SELECT * FROM #{$TB_NOTE} WHERE code=?"
    when 'p', 'png', 'pdf'
      query = "SELECT * FROM #{$TB_MEDIA} WHERE code=?"
    when 'r'
      query = "SELECT * FROM #{$TB_RECIPE} WHERE code=?"
    when 'z'
      query = "SELECT * FROM #{$TB_FCZ} WHERE code=?"
    else
      skip = true
      break;
    end

    unless skip
      r = $DB.prepare( query ).execute( code )
      break unless r.first
    end
  end

  unless code
    puts "Code(x_x)Gen Post"
    exit
  end

  return code
end


#### TAG要素の結合
#将来的に廃止
def bind_tags( res_tag )
    tags = res_tag.first
    sub_class = ''
    sub_class << tags['class1'].sub( '+', '' ) if /\+$/ =~ tags['class1']
    sub_class << tags['class2'].sub( '+', '' ) if /\+$/ =~ tags['class2']
    sub_class << tags['class3'].sub( '+', '' ) if /\+$/ =~ tags['class3']
    tags = "<span class='tagc'>#{sub_class}</span> #{tags['name']} <span class='tag1'>#{tags['tag1']}</span> <span class='tag2'>#{tags['tag2']}</span> <span class='tag3'>#{tags['tag3']}</span> <span class='tag4'>#{tags['tag4']}</span> <span class='tag5'>#{tags['tag5']}</span>"

    return tags
end

#### TAG要素の結合
def tagnames( res_tag )
    sub_class = ''
    sub_class << res_tag['class1'].sub( '+', '' ) if /\+$/ =~ res_tag['class1']
    sub_class << res_tag['class2'].sub( '+', '' ) if /\+$/ =~ res_tag['class2']
    sub_class << res_tag['class3'].sub( '+', '' ) if /\+$/ =~ res_tag['class3']
    tags = "<span class='tagc'>#{sub_class}</span> #{res_tag['name']} <span class='tag1'>#{res_tag['tag1']}</span> <span class='tag2'>#{res_tag['tag2']}</span> <span class='tag3'>#{res_tag['tag3']}</span> <span class='tag4'>#{res_tag['tag4']}</span> <span class='tag5'>#{res_tag['tag5']}</span>"

    return tags
end

#### 特殊数値変換
def convert_zero( t )
  t.to_s.sub!( '(', '' )
  t.to_s.sub!( ')', '' )
  t.to_s.sub!( '†', '' )
  t = 0 if t == nil
  t = 0 if t == ""
  t = 0 if t == '-'
  t = 0 if t == 'Tr'
  t = 0 if t == '*'

  return t
end


#### 食品成分値の処理
def num_opt( num, weight, mode, limit )
  # リミットがない→数値ではない場合はそのまま返す
  return num if limit == nil

    kakko = false
    if /^\(/ =~ num.to_s
      num.sub!( '(', '' )
      num.sub!( ')', '' )
      kakko = true
    end
    ans = BigDecimal( 0 )

  begin
    if num == '-'
      return '-'
    elsif num == 'Tr'
      return 'Tr'
    elsif num == '*'
      return '*'
    elsif num == ''
      return ''
    else
      weight = weight / 100
      #weight_f = 1 if weight_f < 0

      case mode
      when '1'  # 四捨五入
        ans = ( BigDecimal( num ) * weight ).round( limit )
      when '2'  # 切り上げ
        ans = ( BigDecimal( num ) * weight ).ceil( limit )
      when '3'  # 切り捨て
        ans = ( BigDecimal( num ) * weight ).floor( limit )
      else
        ans = ( BigDecimal( num ) * weight ).round( limit )
      end
    end

    if limit == 0
      ans = ans.to_i
    else
      t = ans.to_f.to_s.split( '.' )
      l = t[1].size
      if l != limit
        d = limit - l
        d.times do t[1] << '0' end
      end
      ans = t[0] + '.' + t[1]
    end
    ans = "(#{ans})" if kakko

  rescue
    puts "<span class='error'>[num_opt]ERROR!!<br>"
    puts "num:#{num}<br>"
    puts "weight:#{weight}<br>"
    puts "mode:#{mode}<br>"
    puts "limit:#{limit}</span><br>"
    exit( 9 )
  end

  return ans
end


#### Text washing
def wash( txt )
  txt.gsub!( ';', '' )
  txt.gsub!( "\t", '' )
  txt.gsub!( '<', '&lt;' )
  txt.gsub!( '>', '&gt;' )
  txt.gsub!( '&', '&amp;' )
  txt.gsub!( '"', '&quot;' )
  txt.gsub!( "'", '&#39;' )

  return txt
end


def debug_output( *messages )
  messages.each do |msg|
    puts "#{msg}<br>" if @debug
  end
end


#==============================================================================
# CLASS
#==============================================================================

class Db
  attr_reader :user

  def initialize( user, debug, html )
    @user = user
    @debug = debug
    @html = html
  end

  def qq( query )
    q = query.gsub( ';', '' ) << ';'
    return $DB.query( q )
  end

  def query( query, barrier, arguments = nil )

    puts "<span class='dbq'>[db]#{query},#{arguments}</span><br>" if @debug
    begin
      if @user.status != 0 && @user.barrier && barrier
          puts "<span class='ref_error'>[db]Astral user barrier!</span><br>"
          exit( 9 )
      end

      t = query.chop
      if /[\;\$]/ =~ t
          puts "<span class='error'>[db]ERROR!!</span><br>"
          exit( 9 )
      end

      if arguments.nil?
        return $DB.query( query )
      else
        return $DB.prepare( query ).execute( *arguments )
      end

    rescue
      if @html
        html_init( nil )
        html_head( nil, 0, nil )
      end
        puts "<span class='error'>[db]ERROR!!</span><br>"
    end
  end
end

class User
  attr_accessor :name, :uid, :mom, :mid, :status, :aliasu, :switch, :language, :pass, :mail, :astral, :reg_date, :token
  attr_reader :barrier

  def initialize( cgi = nil )
    @name = cgi.nil? ? '+anonymous+' : cgi.cookies['NAME'].first
    @uid = cgi.nil? ? nil : cgi.cookies[$COOKIE_UID].first
    @mid = nil
    @pass = nil
    @mail = nil
    @reg_date  = nil
    @barrier = false
    @token  = nil

    res = $DB.prepare( "SELECT * FROM #{$TB_USER} WHERE user=? AND cookie=? AND status>0" ).execute( @name, @uid )

    if res.first
      if res.first['status'].to_i == $ASTRAL
        entity_name = @name.sub( '~', '' )
        @barrier = true

        res2 = $DB.prepare( "SELECT * FROM #{$TB_USER} WHERE user=? AND astral=1 AND status>0" ).execute( entity_name )

        if res2.first
          @name = entity_name
          @mid = nil
          @uid = nil
          @mom = nil
          @mid = nil
          @status = $ASTRAL
          @aliasu = nil
          @switch = 0
          @astral = 0
          @language = res.first['language']
        else
          @name = nil
          @uid = nil
          @mom = nil
          @mid = nil
          @status = 0
          @aliasu = nil
          @switch = 0
          @astral = 0
          @language = $DEFAULT_LP
        end
      else
        @status = res.first['status'].to_i
        @aliasu = res.first['aliasu']
        @aliasu = nil if @aliasu == ''
        @mom = res.first['mom']
        @mid = res.first['cookie_m']
        @switch = res.first['switch'].to_i
        @astral = res.first['astral'].to_i
        @language = res.first['language']
        @language = $DEFAULT_LP if @language == nil
        @token = res.first['token']
      end

      @aliasu = @name if @aliasu == nil

    else
      @name = nil
      @uid = nil
      @mom = nil
      @mid = nil
      @status = 0
      @aliasu = nil
      @switch = 0
      @astral = 0
      @language = $DEFAULT_LP
      @barrier = true
    end
  end

  def load_lp( script )
    lp = [nil]
    f = open( "#{$HTDOCS_PATH}/language_/#{script}.#{@language}", "r" )
    f.each do |line| lp << line.chomp.force_encoding( 'UTF-8' ) end
    f.close

    return lp
  end

  def debug()
    puts "name:#{@name}<br>"
    puts "uid:#{@uid}<br>"
    puts "status:#{@status}<br>"
    puts "aliasu:#{@aliasu}<br>"
    puts "mom:#{@mom}<br>"
    puts "mid:#{@mid}<br>"
    puts "language:#{@language}<br>"
    puts "<hr>"
  end
end


class Config
  attr_accessor :val
  def initialize( user, base )
    @user = user
    @base = base.to_s
    @base = 'global' if @base.to_s.empty?
    @elements = {}

    res = $DB.prepare( "SELECT cfgj FROM #{$TB_CFG} WHERE user=?" ).execute( @user.name )&.first
    if res
      begin
        @elements = JSON.parse( res['cfgj'] ) unless res['cfgj'].to_s.empty?
      rescue JSON::ParserError => e
        puts "J(x_x)pE: #{e.message}<br>"
      end     
    else
      $DB.prepare( "INSERT INTO #{$TB_CFG} SET user=?" ).execute( @user.name ) unless @user.barrier
    end

    @elements[ @base ] ||= {}
    @val = @elements[ @base ]
  end

  def base( base )
    @base = base.to_s
    @elements[@base] ||= {}
  end

  def value( key )
    @elements[@base][key] ||= nil
    @elements[@base][key]
  end

  def set_value( key, value )
    @elements[@base][key] ||= {}
    @elements[@base][key] = value
  end

  def set_hash( hash_o )
    @elements[@base] = hash_o
  end

  def update()
    @elements[@base] = @val
    elements_ = JSON.generate( @elements )
    res = $DB.prepare( "SELECT * FROM #{$TB_CFG} WHERE user=?" ).execute( @user.name )
    $DB.prepare( "UPDATE #{$TB_CFG} SET cfgj=? WHERE user=?" ).execute( elements_, @user.name ) unless @user.barrier
  end
end


class MODj
  def initialize( user, mod )
    @user = user
    @mod = mod.to_s
    @json = Hash.new

    res = $DB.prepare( "SELECT json FROM #{$TB_MODJ} WHERE user=? AND module=?" ).execute( @user.name, @mod )&.first
    if res
      begin
        @json = JSON.parse( res['json'] ) unless res['json'].to_s.empty?
      rescue JSON::ParserError => e
        puts "J(x_x)pE: #{e.message}<br>"
      end     
    else
      $DB.prepare( "INSERT INTO #{$TB_MODJ} SET user=?, module=?" ).execute( @user.name, @mod ) if @user.name.to_s != '' && @mod != ''
    end
  end

  def extract()
    return @json
  end

  def permeate( json )
    @json = json
    json_ = JSON.generate( @json )
    $DB.prepare( "UPDATE #{$TB_MODJ} SET json=? WHERE user=? AND module=?" ).execute( json_, @user.name, @mod ) unless @user.barrier
  end
end


class Food
  attr_accessor :code, :name, :group, :classes, :tags

  def initialize( user, code )
    @user = user
    @code = code
    @group = 0
    @sid = ''

    @name = nil
    @classes = []
    @tags = []
    @status = 0

    if /^U/ =~ code
      @fup = 'U'
    elsif /^P/ =~ code
      @fup = 'P'
    elsif /^C/ =~ code
      @fup = 'C'
    else
      @fup = ''
    end
  end

  def load_tag()
    return false if @code.to_s.empty?

    opt = @fup == 'U' ? " AND user='#{@user.name}';" : ''
    res = $DB.prepare( "SELECT * FROM #{$TB_TAG} WHERE FN=? #{opt};" ).execute( @code )&.first
    if res
      @name = res['name']
      @classes[0] = res['class1']
      @classes[1] = res['class2']
      @classes[2] = res['class3']
      @tags[0] = res['tag1']
      @tags[1] = res['tag2']
      @tags[2] = res['tag3']
      @tags[3] = res['tag4']
      @tags[4] = res['tag5']
      @status = res['status'].to_i

      return true
    else
      return false
    end
  end
end


class Sum
  attr_accessor :code, :name, :dish, :protect, :fn, :weight, :unit, :unitv, :check, :init, :rr, :ew

  def initialize( user )
    @user = user
    @code = nil
    @name = nil
    @dish = 1
    @protect = 0
    @fn = nil
    @weight = 0
    @unit = 0
    @unitv = 0
    @check = 0
    @init = ''
    @rr = 1.0
    @ew = 0
  end

  def load_sum( sum )
    t = sum.split( ':' )
    @fn = t[0]
    @weight = t[1]
    @unit = t[2]
    @unitv = t[3]
    @check = t[4]
    @init = t[5]
    if t[6] == nil || t[6] == ''
      @rr = 1.0
    elsif t[6].to_f > 1
      @rr = 1.0
    elsif t[6].to_f < 0
      @rr = 0.0
    else
      @rr = t[6]
    end
    @ew = t[7]
  end

  def load_recipe( code )
    res = $DB.prepare( "SELECT code, name, sum, dish, protect FROM #{$TB_RECIPE} WHERE code=?" ).execute( code )

    @code = res.first['code']
    @name = res.first['name']
    @dish = res.first['dish'].to_i if dish == nil
    @protect = res.first['protect'].to_i
    sum = res.first['sum']
    sum.split( "\t" ).each do |e|
      t = e.split( ':' )
      @fn = t[0]
      @weight = t[1]
      @unit = t[2]
      @unitv = t[3]
      @check = t[4]
      @init = t[5]
      if t[6] == nil || t[6] == ''
        @rr = 1.0
      elsif t[6].to_f > 1
        @rr = 1.0
      elsif t[6].to_f < 0
        @rr = 0.0
      else
        @rr = t[6]
      end
      @ew = t[7]
    end
  end

  def update_db()
    $DB.prepare( "UPDATE #{$TB_SUM} SET code=?, name=?, dish=?, meal=?, protect=?, fn=?, weight=?, unit=?, unitv=?, check=?, init=?, rr=?, ew=? WHERE user=?" ).execute( @code, @name, @dish, @meal, @protect, @fn, @weight, @unit, @unitv, @check, @init, @rr, @ew, @user ) unless @user.barrier

  end

  def debug()
    puts "code:#{code}<br>"
    puts "recipe_name:#{recipe_name}<br>"
    puts "dish_num:#{dish_num}<br>"
    puts "protect:#{protect}<br>"
    puts "sum:#{sum}<br>"
    puts "<hr>"
  end
end


class Recipe
  attr_accessor :code, :user, :branch, :root, :favorite, :public, :protect, :draft, :name, :dish, :type, :role, :tech, :time, :cost, :sum, :protocol, :tags, :comment, :media, :date

  def initialize( user )
    @code = nil
    @user = user
    @branch = 0
    @root = ''
    @favorite = 0
    @public = 0
    @protect = 0
    @draft = 0
    @name = nil
    @dish = 1
    @type = 0
    @role = 0
    @tech = 0
    @time = 0
    @cost = 0
    @sum = ''
    @protocol = ''
    @tags = []
    @comment = ''
    @date = Time.now.strftime("%Y-%m-%d %H:%M:%S")
    @media = []
  end

  def load_cgi( cgi )
    @code = cgi['code']
    @favorite = cgi['favorite'].to_i
    @public = cgi['public'].to_i
    @protect = cgi['protect'].to_i
    @draft = cgi['draft'].to_i
    @name = cgi['recipe_name']
    @type = cgi['type'].to_i
    @role = cgi['role'].to_i
    @tech = cgi['tech'].to_i
    @time = cgi['time'].to_i
    @cost = cgi['cost'].to_i
    @protocol = cgi['protocol']
    @root = cgi['root']

    # excepting for tags
    @protocol.gsub!( '<', '&lt;')
    @protocol.gsub!( '>', '&gt;')
    @protocol.gsub!( ';', '；')
  end

  def load_db( code, mode ) # mode = ture -> from DB directly, mode = false -> from DB res object

    res = nil
    if mode
      return false if code.to_s.empty?

      res = $DB.prepare( "SELECT * FROM #{$TB_RECIPE} WHERE code=?" ).execute( code )

      if res.first
        res = res.first
        @code = code
      else
        puts "<span class='error'>[Recipe load]ERROR!!<br>"
        puts "code:#{@code}</span><br>"

        return false
      end
    else
      res = code
      @code = res['code']
    end

    @user.name = res['user'].to_s
    @branch = res['branch'].to_i
    @root = res['root'].to_s
    @favorite = res['favorite'].to_i
    @public = res['public'].to_i
    @protect = res['protect'].to_i
    @draft = res['draft'].to_i
    @name = res['name'].to_s
    @dish = res['dish'].to_i
    @dish = 1 if @dish.zero?
    @type = res['type'].to_i
    @role = res['role'].to_i
    @tech = res['tech'].to_i
    @time = res['time'].to_i
    @cost = res['cost'].to_i
    @sum = res['sum'].to_s
    @protocol = res['protocol'].to_s
    @date = res['date']

    a = @protocol.split( "\n" )
    if /^\#/ =~ a[0]
      a[0].sub!(  '#', '' )
      a[0].gsub!( "　", "\t" )
      a[0].gsub!( "\s", "\t" )
      @tags = a[0].chomp.split( "\t" )
    end
    @comment = a[1].chomp.sub( '#', '' ) if /^\#/ =~ a[1]

    return res
  end

  def insert_db()
    @name.gsub!( ';', '' )
    @protocol.gsub!( ';', '' )
    @date = @date.strftime( "%Y-%m-%d %H:%M:%S" ) unless @date.kind_of?( String )
    $DB.prepare( "INSERT INTO #{$TB_RECIPE} SET code=?, user=?, dish=?, branch=?, root=?, favorite=?, draft=?, protect=?, public=?, name=?, type=?, role=?, tech=?, time=?, cost=?, sum=?, protocol=?, date=?" ).execute( @code, @user.name, @dish, @branch, @root, @favorite, @draft, @protect, @public, @name, @type, @role, tech, @time, @cost, @sum, @protocol, @date ) unless @user.barrier

  end

  def update_db()
    @name.gsub!( ';', '' )
    @protocol.gsub!( ';', '' )
    @date = @date.strftime( "%Y-%m-%d %H:%M:%S" ) unless @date.kind_of?( String )
    $DB.prepare( "UPDATE #{$TB_RECIPE} SET name=?, dish=?, branch=?, root=?, type=?, role=?, tech=?, time=?, cost=?, sum=?, protocol=?, public=?, favorite=?, protect=?, draft=?, date=? WHERE user=? AND code=?" ).execute( @name, @dish, @branch, @root, @type, @role, @tech, @time, @cost, @sum, @protocol, @public, @favorite, @protect, @draft, @date, @user.name, @code ) unless @user.barrier

  end

  def load_media()
    res = $DB.prepare( "SELECT code FROM #{$TB_MEDIA} WHERE user=? AND origin=? ORDER BY zidx" ).execute( @user.name, @code )

    @media = []
    res.each do |e| @media << e['code'] end
  end

  def delete_db()
    $DB.prepare( "DELETE FROM #{$TB_RECIPE} WHERE user=? AND code=?" ).execute( @user.name, @code ) unless @user.barrier
    $DB.prepare( "DELETE FROM #{$TB_MEDIA} WHERE user=? AND code=?" ).execute( @user.name, @code ) unless @user.barrier
  end

  def tag()
    tags = []
    if /^\#/ =~ @protocol
      a = @protocol.split( "\n" )
      a[0].sub!( '#', '' )
      a[0].gsub!( '　', "\s" )
      tags = a[0].split( "\s" )
      tags.uniq!
    end

    return tags
  end

  def note()
    #note = ''
    #if /^\#/ =~ @protocol
    #  a = @protocol.split( "\n" )
    #  note = a[1].sub( '#', '' ) if /^\#/ =~ a[1]
    #end

    #return note
    return '' unless @protocol.start_with?('#')

    lines = @protocol.lines
    lines[1]&.sub('#', '') || ''
  end

  def debug
    puts "Recipe.code:#{@code}<br>"
    puts "Recipe.name:#{@name}<br>"
    puts "Recipe.favorite:#{@favorite}<br>"
    puts "Recipe.public:#{@public}<br>"
    puts "Recipe.protect:#{@protect}<br>"
    puts "Recipe.draft:#{@draft}<br>"
    puts "Recipe.type:#{@type}<br>"
    puts "Recipe.role:#{@role}<br>"
    puts "Recipe.tech:#{@tech}<br>"
    puts "Recipe.dish:#{@dish}<br>"
    puts "Recipe.time:#{@time}<br>"
    puts "Recipe.cost:#{@cost}<br>"
    puts "Recipe.sum:#{@sum}<br>"
    puts "Recipe.protocol:#{@protocol}<br>"
    puts "Recipe.root:#{@root}<br>"
    puts "Recipe.date:#{@date}<br>"
    puts "Recipe.media:#{@media}<br>"
  end
end



class Tray
  attr_accessor :user, :code, :name, :meal, :protect, :recipes

  def initialize( user )
    @user = user
    @code = nil
    @name = ''
    @meal = ''
    @protect = 0
    @recipes = []

    res = $DB.prepare( "SELECT * from #{$TB_MEAL} WHERE user=?;" ).execute( @user.name )

    if res.first
      @code = res.first['code'].to_s
      @name = res.first['name'].to_s
      @meal = res.first['meal'].to_s
      @protect = res.first['protect'].to_i
      @recipes = @meal.split( "\t" ) unless @meal.empty?
      @recipes.delete_if do |e| e.to_s.strip.empty? end
    end
  end

  def load_menu( code )
    @code = code

    res = $DB.prepare( "SELECT * from #{$TB_MENU} WHERE code=?;" ).execute( code )
    if res.first
      @name = res.first['name'].to_s
      @name = res.first['name'].to_s
      @meal = res.first['meal'].to_s
      @protect = res.first['protect'].to_i
    end
  end

  def add_recipe( recipe_code )
    return if recipe_code.to_s.strip.empty?

    @recipes << recipe_code
    @meal << "\t#{recipe_code}"
  end

  def load_recipe_objs( recipe_objs )
    @recipes = []
    @meal = ''
    unless recipe_objs.empty?
      recipe_objs.each do |o| @recipes << o.code end
      @meal = @recipes.join( "\t" ) 
    end
  end

  def update_db()
    $DB.prepare( "UPDATE #{$TB_MEAL} set code=?, name=?, meal=?, protect=? WHERE user=?;" ).execute( @code, @name, @meal, @protect, @user.name ) unless @user.barrier
  end

  def debug()
    puts "code:#{@code}<br>"
    puts "name:#{@name}<br>"
    puts "meal:#{@meal}<br>"
    puts "protect:#{@protect}<br>"
    puts "recipes:#{@resipes}<br>"
    puts "<hr>"
  end
end


class Menu
  attr_accessor :user, :code, :name, :meal, :protect, :public, :label, :memo, :media

  def initialize( user )
    @code = nil
    @user = user
    @name = nil
    @meal = nil
    @protect = 0
    @public = 0
    @label = nil
    @memo = nil
    @media = []
  end

  def load_cgi( cgi )
    @code = cgi['code'].to_s
    @name = cgi['menu_name'].to_s
    @protect = cgi['protect'].to_i
    @public = cgi['public'].to_i
    @label = cgi['label'].to_s
    @memo = cgi['memo'].to_s

    # excepting for tags
#    @memo.gsub!( '<', '&lt;')
#    @memo.gsub!( '>', '&gt;')
#    @memo.gsub!( ';', '；')
    @memo = wash( @memo )
  end

  def load_db( code, mode )
    if mode
      return false if code.to_s.empty?

      # DB
      res = $DB.prepare( "SELECT * FROM #{$TB_MENU} WHERE code=? AND user=?" ).execute( code, @user.name )
      res = res.first
    else
      res = code
    end

    if res
      @code = res['code'].to_s
      @user.name = res['user'].to_s
      @name = res['name'].to_s
      @meal = res['meal'].to_s
      @label = res['label'].to_s
      @protect = res['protect'].to_i
      @public = res['public'].to_i
      @memo = res['memo'].to_s
    else
      puts "<span class='error'>[Menu load]ERROR!!<br>"
      puts "code:#{@code}</span><br>"

      return false
    end

    return res
  end

  def load_media()
    res = $DB.prepare( "SELECT code FROM #{$TB_MEDIA} WHERE user=? AND origin=?" ).execute( @user.name, @origin )

    @media = []
    res.each do |e| @media << e['code'] end
  end

  def insert_db()
    $DB.prepare( "INSERT INTO #{$TB_MENU} SET code=?, user=?, public=?, protect=?, label=?, name=?, meal=?, memo=?" ).execute( @code, @user.name, @public, @protect, @label, @name, @meal, @memo ) unless @user.barrier

  end

  def update_db()
    $DB.prepare( "UPDATE #{$TB_MENU} SET public=?, protect=?, label=?, name=?, meal=?, memo=? WHERE user=? AND code=?" ).execute( @public, @protect, @label, @name, @meal, @memo, @user.name, @code ) unless @user.barrier

  end

  def delete_db()
    $DB.prepare( "DELETE FROM #{$TB_MENU} WHERE user=? AND code=?" ).execute( @user.name, @code ) unless @user.barrier
    $DB.prepare( "DELETE FROM #{$TB_MEDIA} WHERE user=? AND origin=?" ).execute( @user.name, @code ) unless @user.barrier

  end

  def debug()
    puts "code:#{@code}<br>"
    puts "user:#{@user.name}<br>"
    puts "name:#{@name}<br>"
    puts "protect:#{@protect}<br>"
    puts "public:#{@public}<br>"
    puts "meal:#{@meal}<br>"
    puts "label:#{@label}<br>"
    puts "memo:#{@memo}<br>"
    puts "media:#{@media}<br>"
    puts "<hr>"
  end
end
