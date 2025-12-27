#! /usr/bin/ruby
# coding: utf-8
#Nutrition browser 2020 index page 0.5.1 (2025/08/11)


#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    nb: '栄養ブラウザ',
    login: 'ログイン',
    logout: 'ログアウト',
    regist: '登録',
    san: 'さん',
    help: '<img src=\'bootstrap-dist/icons/question-circle-gray.svg\' style=\'height:3em; width:2em;\'>',
    search: '<img src=\'bootstrap-dist/icons/search-gray.svg\' style=\'height:1.5em; width:2em;\'>',
    food: '食品',
    recipe: 'レシピ',
    memory: '記憶',
    login_: 'ログインが必要',
    gmen: 'ギルドメンバー専用',
    cboard: '<img src=\'bootstrap-dist/icons/card-text.svg\' style=\'height:1.2em; width:1.2em;\'>&nbsp;まな板',
    table: '<img src=\'bootstrap-dist/icons/motherboard.svg\' style=\'height:1.2em; width:1.2em;\'>&nbsp;お膳',
    history: '<img src=\'bootstrap-dist/icons/inbox-fill.svg\' style=\'height:1.2em; width:1.2em;\'>&nbsp;履　歴',
    recipel: '<img src=\'bootstrap-dist/icons/journal-text.svg\' style=\'height:1.2em; width:1.2em;\'>&nbsp;レシピ帳',
    menul: '<img src=\'bootstrap-dist/icons/journals.svg\' style=\'height:1.2em; width:1.2em;\'>&nbsp;献立帳',
    book: '<img src=\'bootstrap-dist/icons/book.svg\' style=\'height:1.2em; width:1.2em;\'>',
    gear: '<img src=\'bootstrap-dist/icons/gear-fill.svg\' style=\'height:1.2em; width:1.2em;\'>',
    fire: '<img src=\'bootstrap-dist/icons/fire-blue.svg\' style=\'height:0.8em; width:1.2em;\'>',
    ping: '<img src=\'bootstrap-dist/icons/fire-blue.svg\' style=\'height:0.8em; width:1.2em;\'>',
    piny: '<img src=\'bootstrap-dist/icons/fire-blue.svg\' style=\'height:0.8em; width:1.2em;\'>',
    koyomi: 'こよみ',
    ginmi: 'アセスメント',
    pysique: '体格管理',
    momchai: '母子管理',
    note: '管理ノート',
    foodrank: '食品栄養ランク',
    fczl: 'FCZエディタ',
    mjl: 'JSONエディタ',
    medial: 'メディアエディタ',
    accountm: '娘アカウント管理',
    astral: '幽体管理',
    visionnerz: 'VISIONNERZ',
    recipe3d: '3Dレシピ検索',
    school: 'お料理教室',
    toker: '統計(R)',
    unit: '単位登録',
    color: '色登録',
    allergen: 'アレルゲン登録',
    dic: '辞書登録',
    slog: '別リク',
    user: 'ユーザー管理',
    bond: '絆管理',
    gycv: '緑黄色野菜登録',
    shun: '旬登録',
    memorya: '記憶管理',
    senior: '黄昏管理',
    condition: '状態管理',
    intake: '食事摂取基準',
    tensei: '転生管理',
    fflow: '食品フロー'
  }

  return l[language]
end

#### HTML top
def html_top( user, l, db )
  puts 'HTML TOP<br>' if @debug
  user_name = user.name
  user_name = user.aliasu if user.aliasu != '' && user.aliasu != nil

  case user.status
  when 1
    login_color = "primary"
  when 3, 6
    login_color = "warning"
  when 2, 4
    login_color = "info"
  when 5
    login_color = "success"
  when 8, 9
    login_color = "danger"
  when 7
    login_color = "light"
  else
    login_color = "secondary"
  end
  login_color = "light" if user.name == 'gm'

  family = []
  family_a = []

  r = db.query( "SELECT * FROM user WHERE mom=? AND status='6' AND switch=1;", false, [user.name] )
  # Dose user have doughters?
  if r.first
    puts 'MOM with family<br>' if @debug
    family << user.name
    t = ( t == '' || t == nil ) ? user.name : user.aliasu
    family_a << t

    r.each do |e|
      family << e['user']
      family_a << e['aliasu'].to_s
    end
  else
    res = db.query( "SELECT * FROM user WHERE cookie=? AND ( status='5' OR status>='8' );", false, [user.mid] )&.first
    if res
      puts 'One of family<br>' if @debug
      family << res['user']
      t = ( t == '' || t == nil ) ? res['user'] : res['aliasu']
      family_a << t

      res2 = db.query( "SELECT * FROM user WHERE mom=? AND status='6' AND switch=1;", false, [res['user']] )
      res2.each do |e|
        family << e['user']
        family_a << e['aliasu'].to_s
      end
    end
  end

  login = ''
  if family.size > 0
    puts 'family mode<br>' if @debug
    login = "<div class='form-inline'>"
    login << "<SELECT style='background-color:#343a40' id='login_mv' class='custom-select text-#{login_color}' onchange=\"chageAccountM()\">"
    family.size.times do |c|
      t = ( family_a[c] != nil && family_a[c] != '' ) ? family_a[c] : family[c]
      login << "<OPTION value='#{family[c]}' #{$SELECT[family[c] == user.name]}>#{t}</OPTION>"
    end
    login << "</SELECT>"
    login << "&nbsp;#{l[:san]}&nbsp;|&nbsp;<a href=\"login.cgi?mode=logout\" class=\"text-#{login_color}\">#{l[:logout]}</a>"
    login << "</div>"
  else
    puts 'solo mode<br>' if @debug
    user_name = l[:fire] + user_name + l[:fire] if user.status == 7
    login = "#{user_name}&nbsp;#{l[:san]}&nbsp;|&nbsp;<a href=\"login.cgi?mode=logout\" class=\"text-#{login_color}\">#{l[:logout]}</a>"
  end
  login = "<a href='login.cgi' class=\"text-#{login_color}\">#{l[:login]}</a>&nbsp;|&nbsp;<a href=\"regist.cgi\" class=\"text-#{login_color}\">#{l[:regist]}</a>" if user_name == nil

  puts 'HTML HEAD<br>' if @debug

  ##
##
html = <<-"HTML"
<header class="navbar navbar-expand-lg navbar-dark bg-dark" id="header">
  <div class="container-fluid">
    <a href="index.cgi" class="navbar-brand h1 text-#{login_color}">#{l[:nb]}</a>
    <span class="navbar-text text-#{login_color} login_msg h4">#{login}</span>
    <span id='HELP'></span>
    <span class="d-flex">
      <select class="form-select" id="qcate">
        <option value='0'>#{l[:food]}</option>
        <option value='1'>#{l[:recipe]}</option>
        <option value='2'>#{l[:memory]}</option>
      </select>
      <input class="form-control" type="text" maxlength="100" id="words" onchange="search()">
      <btton class='btn btn-sm' onclick="search()">#{l[:search]}</button>
    </span>
  </div>
</header>
HTML
##
  ##
  puts html
end

#### HTML nav
def html_nav( user, l, db )
  cb_num = '-'
  mt_num = '-'
  # まな板カウンター
  if user.name
    res = db.query( "SELECT sum from #{$TB_SUM} WHERE user=?", false, [user.name] )&.first
    if res
      t = res['sum']&.split( "\t" ) || []
      cb_num = t.size
    else
      db.query( "INSERT INTO #{$TB_SUM} SET user=?", false, [user.name] )
      cb_num = 0
    end
    # 献立カウンター

    res = db.query( "SELECT meal from #{$TB_MEAL} WHERE user=?", false, [user.name] )&.first
    if res
      t = res['meal']&.split( "\t" ) || []
      mt_num = t.size
    else
      db.query( "INSERT INTO #{$TB_MEAL} SET user=?", false, [user.name] )
      mt_num = 0
    end
  end

  # 履歴ボタンとまな板ボタンの設定
  if user.status >= 1
    cb = "#{l[:cboard]} <span class='badge rounded-pill bg-dark text-light' id='CBN'>#{cb_num}</span>"
    mb = "#{l[:table]} <span class='badge rounded-pill bg-dark text-light' id='MTN'>#{mt_num}</span>"
    special_button = "<button type='button' class='btn btn-outline-dark btn-sm nav_button' id='category0' onclick='summonL1( 0 )''>#{@category[0]}</button>"
    his_button = "<button type='button' class='btn btn-primary btn-sm nav_button' onclick=\"initHistory( 'init' )\">#{l[:history]}</button>"
    sum_button = "<button type='button' class='btn btn-outline-dark btn-sm nav_button' onclick=\"initCB( 'init' )\">#{cb}</button>"
    recipe_button = "<button type='button' class='btn btn-outline-dark btn-sm nav_button' onclick=\"recipeList( 'init' )\">#{l[:recipel]}</button>"
    menu_button = "<button type='button' class='btn btn-outline-dark btn-sm nav_button' onclick=\"initMT( 'init' )\">#{mb}</button>"
    set_button = "<button type='button' class='btn btn-outline-dark btn-sm nav_button' onclick=\"menuList( 'init' )\">#{l[:menul]}</button>"
    config_button = "<button type='button' class='btn btn-outline-dark btn-sm nav_button' onclick=\"configInit( 'init' )\">#{l[:gear]}</button>"
  else
    cb = "#{l[:cboard]} <span class='badge badge-pill badge-secondary' id='CBN'>#{cb_num}</span>"
    mb = "#{l[:table]} <span class='badge badge-pill badge-secondary' id='MTN'>#{mt_num}</span>"
    special_button = "<a href='login.cgi'><button type='button' class='btn btn-dark btn-sm nav_button text-secondary'>#{@category[0]}</button></a>"
    his_button = "<a href='login.cgi'><button type='button' class='btn btn-dark btn-sm nav_button text-secondary'>#{l[:history]}</button></a>"
    sum_button = "<a href='login.cgi'><button type='button' class='btn btn-dark btn-sm nav_button text-secondary'>#{cb}</button></a>"
    recipe_button = "<a href='login.cgi'><button type='button' class='btn btn-dark btn-sm nav_button text-secondary'>#{l[:recipel]}</button></a>"
    menu_button = "<a href='login.cgi'><button type='button' class='btn btn-dark btn-sm nav_button text-secondary'>#{mb}</button></a>"
    set_button = "<a href='login.cgi'><button type='button' class='btn btn-dark btn-sm nav_button text-secondary'>#{l[:menul]}</button></a>"
    config_button = "<a href='login.cgi'><button type='button' class='btn btn-dark btn-sm nav_button text-secondary'>#{l[:gear]}</button></a>"
  end

  if user.status >= 2
    g_button = "<button type='button' class='btn btn-warning btn-sm nav_button text-warning guild_color' onclick=\"changeMenu( '#{user.status}' )\">G</button>"
  else
    g_button = "<button type='button' class='btn btn-warning btn-sm nav_button text-dark guild_color' onclick=\"displayVIDEO( '#{l[:gmen]}' )\">G</button>"
  end

  gm_account = ''
  if user.status == 9
    gm_account << "<button type='button' class='btn btn-warning btn-sm nav_button master_color' onclick=\"initAccount( 'init' )\">#{l[:user]}</button>"
    gm_account << "<button type='button' class='btn btn-warning btn-sm nav_button master_color' onclick=\"initBond( 'init' )\">#{l[:bond]}</button>"

  end

  ##
##
html = <<-"HTML"
<nav class='container-fluid'>
    #{g_button}
    <button type="button" class="btn btn-info btn-sm nav_button" id="category1" onclick="summonL1( 1 )">#{@category[1]}</button>
    <button type="button" class="btn btn-info btn-sm nav_button" id="category2" onclick="summonL1( 2 )">#{@category[2]}</button>
    <button type="button" class="btn btn-info btn-sm nav_button" id="category3" onclick="summonL1( 3 )">#{@category[3]}</button>
    <button type="button" class="btn btn-danger btn-sm nav_button" id="category4" onclick="summonL1( 4 )">#{@category[4]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button" id="category5" onclick="summonL1( 5 )">#{@category[5]}</button>
    <button type="button" class="btn btn-success btn-sm nav_button" id="category6" onclick="summonL1( 6 )">#{@category[6]}</button>
    <button type="button" class="btn btn-info btn-sm nav_button" id="category7" onclick="summonL1( 7 )">#{@category[7]}</button>
    <button type="button" class="btn btn-success btn-sm nav_button" id="category8" onclick="summonL1( 8 )">#{@category[8]}</button>
    <button type="button" class="btn btn-success btn-sm nav_button" id="category9" onclick="summonL1( 9 )">#{@category[9]}</button>
    <button type="button" class="btn btn-danger btn-sm nav_button" id="category10" onclick="summonL1( 10 )">#{@category[10]}</button>
    <button type="button" class="btn btn-danger btn-sm nav_button" id="category11" onclick="summonL1( 11 )">#{@category[11]}</button>
    <button type="button" class="btn btn-danger btn-sm nav_button" id="category12" onclick="summonL1( 12 )">#{@category[12]}</button>
    <button type="button" class="btn btn-outline-secondary btn-sm nav_button" id="category13" onclick="summonL1( 13 )">#{@category[13]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button" id="category14" onclick="summonL1( 14 )">#{@category[14]}</button>
    <button type="button" class="btn btn-secondary btn-sm nav_button" id="category15" onclick="summonL1( 15 )">#{@category[15]}</button>
    <button type="button" class="btn btn-primary btn-sm nav_button" id="category16" onclick="summonL1( 16 )">#{@category[16]}</button>
    <button type="button" class="btn btn-outline-secondary btn-sm nav_button" id="category17" onclick="summonL1( 17 )">#{@category[17]}</button>
    <button type="button" class="btn btn-secondary btn-sm nav_button" id="category18" onclick="summonL1( 18 )">#{@category[18]}</button>
    #{special_button}
    #{his_button}
    #{sum_button}
    #{recipe_button}
    #{menu_button}
    #{set_button}
    <button type="button" class="btn btn-outline-secondary btn-sm nav_button" onclick="bookOpen( 'books/books.html', 1 )">#{l[:book]}</button>
    #{config_button}
</nav>
<nav class='container-fluid' id='guild_menu' style='display:none;'>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="initKoyomi()">#{l[:koyomi]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="foodRank()">#{l[:foodrank]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="initRefIntake()">#{l[:intake]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="initGinmi()">#{l[:ginmi]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="initPhysique()">#{l[:pysique]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="initMomChai()">#{l[:momchai]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="initFCZlist()">#{l[:fczl]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="initMemoryList( 'init' )">#{l[:memorya]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button guild_color" onclick="initNote()">#{l[:note]}</button>
</nav>
<nav class='container-fluid' id='gs_menu' style='display:none;'>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="initAccountM()">#{l[:accountm]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="initAstral()">#{l[:astral]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="recipe3ds()">#{l[:recipe3d]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="initSchool()">#{l[:school]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="initToker()">#{l[:toker]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="initMedialist()">#{l[:medial]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="initFFlow()">#{l[:fflow]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="">#{l[:senior]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="">#{l[:condition]}</button>
    <button type="button" class="btn btn-dark btn-sm nav_button shun_color" onclick="">#{l[:mjl]}</button>
</nav>
<nav class='container-fluid' id='gm_menu' style='display:none;'>
    <button type="button" class="btn btn-warning btn-sm nav_button master_color" onclick="initUnit( 'init' )">#{l[:unit]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button master_color" onclick="initColor( 'init' )">#{l[:color]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button master_color" onclick="initAllergen()">#{l[:allergen]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button master_color" onclick="initGYCV( 'init' )">#{l[:gycv]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button master_color" onclick="initShun( 'init' )">#{l[:shun]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button master_color" onclick="initDic( 'init' )">#{l[:dic]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button master_color" onclick="initSlogf( 'init' )">#{l[:slog]}</button>
    <button type="button" class="btn btn-warning btn-sm nav_button master_color" onclick="initTensei( 'init' )">#{l[:tensei]}</button>
    #{gm_account}
</nav>
HTML
##
  ##

  puts html
end


#### HTML working space
def html_working( title )
  ##
##
html = <<-"HTML"
<div class="bw_frame" id='WORLD' aligh="center">
  <div class="line" id='LINE' style="display: none;"></div>
  <div class="browse_window" id='L1' style="display: block;">#{title}</div>
  <div class="browse_window" id='L2' style="display: none;"></div>
  <div class="browse_window" id='L3' style="display: none;"></div>
  <div class="browse_window" id='L4' style="display: none;"></div>
  <div class="browse_window" id='L5' style="display: none;"></div>
  <div class="browse_window" id='LF' style="display: none;"></div>
  <div class="browse_window" id='LM' style="display: none;"></div>
</div>

<!-- Modal window -->
<div class="modal fade" id="modal" tabindex="-1" aria-labelledby="modal_label" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-body" id='modal_body'></div>
    </div>
  </div>
</div>

<!-- Modal tip -->
<div class="modal fade" id="modal_tip" tabindex="-2" aria-labelledby="modal_tip_label" aria-hidden="true">
  <div class="modal-dialog modal-md modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-body" id='modal_tip_body'></div>
    </div>
  </div>
</div>

<!-- VIDEO -->
<div class="video" id='VIDEO' style="display: none;"></div>

HTML
##
  ##

  puts html
end


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.status = 0 unless user.name
user.debug if @debug
l = language_pack( user.language )

unless l
  puts '(Ux_xL)' 
  exit
end
db = Db.new( user, @debug, false )

res = db.query( "SELECT ifix FROM cfg WHERE user=?", false, [user.name] )&.first
ifix = res.nil? ? 0 : res['ifix']&.to_i

html_head( nil, user.status, nil )

puts "<div style='position:fixed; z-index:100; background-color:white'>" if ifix == 1

html_top( user, l, db )
html_nav( user, l, db )


if ifix == 1
  puts '</div>'
  puts '<header class="navbar navbar-dark bg-dark"><h4> </h4></header>'
  puts "<button type='button' class='btn btn btn-outline-light btn-sm nav_button'> </button><br>"
  puts "<button type='button' class='btn btn btn-outline-light btn-sm nav_button'> </button><br>"
end

if user.status >= 2 && ifix == 1
  puts "<button type='button' class='btn btn btn-outline-light btn-sm nav_button'> </button><br>"
  puts "<button type='button' class='btn btn btn-outline-light btn-sm nav_button'> </button><br>"
  puts "<button type='button' class='btn btn btn-outline-light btn-sm nav_button'> </button><br>"
  puts "<button type='button' class='btn btn btn-outline-light btn-sm nav_button'> </button><br>"
end

html_working( html_title())

html_foot()
