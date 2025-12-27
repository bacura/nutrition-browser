#Nutrition browser 2020 soul Japanese pack 0.3.2 (2025/12/27)

#==============================================================================
# STATIC
#==============================================================================
@category = %w( 特　殊 穀　類 いも・でん粉類 砂糖・甘味類 豆　類 種実類 野菜類 果実類 きのこ類 藻　類 魚介類 肉　類 卵　類 乳　類 油脂類 菓子類 し好飲料類 調味料・香辛料類 調理・流通食品類 特　殊 )
@fg = %w( 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 )

@fct_base = %w( FG FN SID Tagnames )
@fct_rew = %w( REFUSE ENERC ENERC_KCAL WATER )
@fct_ew = %w( ENERC ENERC_KCAL WATER )
@fct_pf = %w( PROTCAA PROT PROTV FAT FATNLEA FATV FASAT FAMS FAPU FAPUN3 FAPUN6 CHOLE )
@fct_cho = %w( CHOCDF CHOAVLM CHOAVL CHOAVLDF CHOV FIB FIBTG FIBSOL FIBINS FIBTDF FIBSDFS FIBSDFP FIBIDF STARES POLYL OA )
@fct_m = %w( ASH NA K CA MG P FE ZN CU MN ID SE CR MO )
@fct_fsv = %w( RETOL CARTA CARTB CRYPXB CARTBEQ VITA_RAE VITD TOCPHA TOCPHB TOCPHG TOCPHD VITK )
@fct_wsv = %w( THIA RIBF NIA NE VITB6A VITB12 FOL PANTAC BIOT VITC  )
@fct_as = %w( ALC NACL_EQ )
@fct_para = %w( ENERC_KCAL WATER PROTV FATV FASAT CHOV FIB CA FE CARTBEQ THIA RIBF NACL_EQ )
@fct_min = @fct_rew + @fct_pf + @fct_cho + @fct_m + @fct_fsv + @fct_wsv + @fct_as
@fct_min_nr = @fct_ew + @fct_pf + @fct_cho + @fct_m + @fct_fsv + @fct_wsv + @fct_as
@fct_item = @fct_base + @fct_min
@fct_item << 'Notice'
@fct_d

#             0              1                 2                 3                     4                  5                        6                               7               8                                   9                    10                       11             12                                 13                14                      15                        16                          17                               18                               19                    20                    21                                    22                                  23                                      24                      25                    26                         27                           28                            29                          30                                    31                                    32                            33                          34                     35             36               37           38                39                 40          41            42            43          44              45             46            47            48              49                  50                  51                  52                          53                          54                           55                56                      57                        58                       59                      60                61                  62                 63                64                    65                   66                     67            68                     69               70                71              72              73                       74
@fct_name = {'FG'=>'食品群', 'FN'=>'食品番号', 'SID'=>'索引番号', 'Tagnames'=>'食品名', 'REFUSE'=>'廃棄率', 'ENERC'=>'エネルギー(kJ)',  'ENERC_KCAL'=>'エネルギー(kcal)',  'WATER'=>'水分', 'PROTCAA'=>'アミノ酸組成によるたんぱく質', 'PROT'=>'たんぱく質',  'PROTV'=>'たんぱく質*',   'FAT'=>'脂質',  'FATNLEA'=>'トリアシルグリセロール当量',  'FATV'=>'脂質*', 'FASAT'=>'飽和脂肪酸', 'FAMS'=>'一価不飽和脂肪酸', 'FAPU'=>'多価不飽和脂肪酸',  'FAPUN3'=>'n-3系多価不飽和脂肪酸', 'FAPUN6'=>'n-6系多価不飽和脂肪酸', 'CHOLE'=>'コレステロール', 'CHOCDF'=>'炭水化物', 'CHOAVLM'=>'利用可能炭水化物(単糖当量)', 'CHOAVL'=>'利用可能炭水化物(質量計)', 'CHOAVLDF'=>'利用可能炭水化物(差引き法)', 'CHOV'=>'炭水化物*',  'FIB'=>'食物繊維総量', 'FIBTG'=>'食物繊維総量(P)', 'FIBSOL'=>'水溶性食物繊維(P)', 'FIBINS'=>'不溶性食物繊維(P)', 'FIBTDF'=>'食物繊維総量(A)', 'FIBSDFS'=>'低分子量水溶性食物繊維(A)', 'FIBSDFP'=>'高分子量水溶性食物繊維(A)', 'FIBIDF'=>'不溶性食物繊維(A)', 'STARES'=>'難消化性でん粉(A)', 'POLYL'=>'糖アルコール', 'ASH'=>'灰分',  'NA'=>'ナトリウム', 'K'=>'カリウム', 'CA'=>'カルシウム', 'MG'=>'マグネシウム', 'P'=>'リン',  'FE'=>'鉄',   'ZN'=>'亜鉛', 'CU'=>'銅', 'MN'=>'マンガン', 'ID'=>'ヨウ素', 'SE'=>'セレン', 'CR'=>'クロム', 'MO'=>'モリブデン', 'RETOL'=>'レチノール', 'CARTA'=>'α-カロテン', 'CARTB'=>'β-カロテン', 'CRYPXB'=>'β-クリプトキサンチン', 'CARTBEQ'=>'β-カロテン当量', 'VITA_RAE'=>'レチノール活性当量', 'VITD'=>'ビタミンD', 'TOCPHA'=>'α-トコフェロール', 'TOCPHB'=>'β-トコフェロール',  'TOCPHG'=>'γ-トコフェロール', 'TOCPHD'=>'δ-トコフェロール', 'VITK'=>'ビタミンK', 'THIA'=>'ビタミンB1', 'RIBF'=>'ビタミンB2', 'NIA'=>'ナイアシン', 'NE'=>'ナイアシン当量',   'VITB6A'=>'ビタミンB6', 'VITB12'=>'ビタミンB12', 'FOL'=>'葉酸', 'PANTAC'=>'パントテン酸', 'BIOT'=>'ビオチン', 'VITC'=>'ビタミンC', 'OA'=>'有機酸', 'ALC'=>'アルコール', 'NACL_EQ'=>'食塩相当量', 'Notice'=>'備考'}
@fct_unit = {'FG'=>nil,     'FN'=>nil,        'SID'=>nil,       'Tagnames'=>nil,      'REFUSE'=>'%',     'ENERC'=>'kJ',           'ENERC_KCAL'=>'kcal',           'WATER'=>'g',   'PROTCAA'=>'g',                     'PROT'=>'g',         'PROTV'=>'g',             'FAT'=>'g',    'FATNLEA'=>'g',                    'FATV'=>'g',       'FASAT'=>'g',          'FAMS'=>'g',              'FAPU'=>'g',               'FAPUN3'=>'g',                    'FAPUN6'=>'g',                   'CHOLE'=>'mg',        'CHOCDF'=>'g',        'CHOAVLM'=>'g',                       'CHOAVL'=>'g',                       'CHOAVLDF'=>'g',                       'CHOV'=>'g',            'FIB'=>'g',           'FIBTG'=>'g',              'FIBSOL'=>'g',               'FIBINS'=>'g',                'FIBTDF'=>'g',              'FIBSDFS'=>'g',                       'FIBSDFP'=>'g',                       'FIBIDF'=>'g',                'STARES'=>'g',               'POLYL'=>'g',         'ASH'=>'g',    'NA'=>'mg',      'K'=>'mg',    'CA'=>'mg',      'MG'=>'mg',        'P'=>'mg',   'FE'=>'mg',  'ZN'=>'mg',   'CU'=>'mg', 'MN'=>'mg',    'ID'=>'μg',    'SE'=>'μg',   'CR'=>'μg',   'MO'=>'μg',      'RETOL'=>'μg',      'CARTA'=>'μg',      'CARTB'=>'μg',       'CRYPXB'=>'μg',             'CARTBEQ'=>'μg',          'VITA_RAE'=>'μg',             'VITD'=>'μg',     'TOCPHA'=>'mg',          'TOCPHB'=>'mg',          'TOCPHG'=>'mg',          'TOCPHD'=>'mg',          'VITK'=>'μg',     'THIA'=>'mg',      'RIBF'=>'mg',      'NIA'=>'mg',      'NE'=>'mg',           'VITB6A'=>'mg',      'VITB12'=>'μg',        'FOL'=>'μg',   'PANTAC'=>'mg',       'BIOT'=>'μg',    'VITC'=>'mg',     'OA'=>'g',      'ALC'=>'g',      'NACL_EQ'=>'g',          'Notice'=>nil}
@fct_frct = {'FG'=>nil,     'FN'=>nil,        'SID'=>nil,       'Tagnames'=>nil,      'REFUSE'=>nil,     'ENERC'=>0,              'ENERC_KCAL'=>0,                'WATER'=>1,     'PROTCAA'=>1,                       'PROT'=>1,           'PROTV'=>1,               'FAT'=>1,      'FATNLEA'=>1,                      'FATV'=>1,         'FASAT'=>2,            'FAMS'=>2,                'FAPU'=>2,                 'FAPUN3'=>2,                      'FAPUN6'=>2,                     'CHOLE'=>0,           'CHOCDF'=>1,          'CHOAVLM'=>1,                         'CHOAVL'=>1,                         'CHOAVLDF'=>1,                         'CHOV'=>1,              'FIB'=>1,             'FIBTG'=>1,                'FIBSOL'=>1,                 'FIBINS'=>1,                  'FIBTDF'=>1,                'FIBSDFS'=>1,                        'FIBSDFP'=>1,                         'FIBIDF'=>1,                  'STARES'=>1,                 'POLYL'=>1,           'ASH'=>1,      'NA'=>0,         'K'=>0,       'CA'=>0,         'MG'=>0,           'P'=>0,      'FE'=>1,     'ZN'=>1,      'CU'=>2,    'MN'=>2,       'ID'=>0,       'SE'=>0,      'CR'=>0,      'MO'=>0,         'RETOL'=>0,         'CARTA'=>0,         'CARTB'=>0,          'CRYPXB'=>0,                'CARTBEQ'=>0,             'VITA_RAE'=>0,                'VITD'=>1,        'TOCPHA'=>1,             'TOCPHB'=>1,             'TOCPHG'=>1,             'TOCPHD'=>1,             'VITK'=>0,        'THIA'=>2,         'RIBF'=>2,         'NIA'=>1,         'NE'=>1,              'VITB6A'=>2,         'VITB12'=>1,           'FOL'=>0,      'PANTAC'=>2,          'BIOT'=>1,       'VITC'=>0,        'OA'=>1,        'ALC'=>1,        'NACL_EQ'=>1,            'Notice'=>nil}

@palette_default_name = %w( 簡易表示用 基本の5成分 基本の12成分 基本の21成分 全て )
@palette_default = %w( 00000010001001000000000010000000000000000000000000000000000000000000000001 00000010001001000000000010000000000000000000000000000000000000000000000001 00000010001001000000000011000000000001100100000000000001000001100000000001 00000010001001000000000011000000000001110111000000000001000001101111001011 00001111111111111111111111111111111111111111111111111111111111111111111111 )

$PALETTE_DEFAULT = { 'jp' => @palette_default }
@palette_bit_all = [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1 ]

@recipe_type = %w( 未設定 日本の料理（和食） 日本の料理（洋食） 中華な料理 イタリアの料理 フランスの料理 エスニックな料理 西洋ぽい料理 謎な料理 )
@recipe_role = %w( 未設定 主食（兼主菜） 主菜 副菜 汁物 デザート・おやつ 飲み物 調味料 離乳食 ベース )
@recipe_tech = %w( 未設定 茹でる・煮る・炊く 直火・炙る 炒める・ソテー 蒸す 揚げる 和える 生・非加熱 冷蔵・冷凍 オーブン・グリル 電子レンジ )
@recipe_time = %w( 未設定 ～5分 ～10分 ～15分 ～20分 ～30分 ～45分 ～60分 ～120分 121分～ )
@recipe_cost = %w( 未設定 ～50円 ～100円 ～150円 ～200円 ～300円 ～400円 ～500円 ～600円 ～800円 ～1000円 1000円～ )

#               0    1           2    3    4    5
@sub_group = %w( '' 緑黄色野菜 普通牛乳 味噌 醤油 食塩 )

#             0    1   2    3    4  5  6  7  8 9  10 11
#@color = %w( 未指定 赤 ピンク オレンジ 黄 緑 青 紫 茶 白 黒 透明 )

#             0      1   2     　3     4       5       6  7   8      9
@account = %w( 退会 一般 常ギルメン guest 萌ギルメン 旬ギルメン 娘 幽体 サブマス ギルマス )
@accounts_general = [1, 2, 4, 5]
@accounts_guild = [2, 4, 5]
$GUEST = 3
$ASTRAL = 7
$DAUGHTER = 6

#             0                1                   2                 3                4             5                 6                7                     8              9               10                   11                  12                  13                14               15                   16                     17                     18             19             20             21             22             23
@kex_std = { '身長'=>'cm', '体重'=>'kg', 'BMI'=>'', '体脂肪率'=>'%', '腹囲'=>'cm', 'ブリストルスケール'=>'','歩数'=>'歩', 'METs'=>'', 'Δエネルギー'=>'kcal', '収縮期血圧'=>'mmHg', '拡張期血圧'=>'mmHg', '空腹時血糖'=>'mg/dl', 'HbA1c'=>'%', '中性脂肪'=>'mg/dL', '総コレステロール'=>'mg/dL', 'LDL'=>'mg/dL', 'HDL'=>'mg/dL', '尿酸'=>'mg/dL',  'AST'=>'IU/L',  'ALT'=>'IU/L',  'ALP'=>'IU/L',  'LDH'=>'IU/L',  'γ-GTP'=>'IU/L' }
@kex_presets = Hash.new
@kex_presets['体格管理'] = '{"kexu":{"体重":"kg","体脂肪率":"%","Δエネルギー":"kcal"},"kexa":{"体重":"1","体脂肪率":"1","Δエネルギー":"1"},"kexg":{},"kexup":{},"kexbtm":{}}'

#
@something = {'?--'=>'何か食べた（微盛）', '?-'=>'何か食べた（小盛）', '?='=>'何か食べた（並盛）', '?+'=>'何か食べた（大盛）', '?++'=>'何か食べた（特盛）', '?0'=>'何も食べない', '?P'=>'写真のみ'}

#==============================================================================
# HTML header
#==============================================================================
def html_head( interrupt, status, sub_title )
  refresh = ''
  refresh = '<meta http-equiv="refresh" content="0; url=index.cgi">' if interrupt == 'refresh'

  js_guild = ''
  if status >= 2
    js_guild = "<script type='text/javascript' src='#{$JS_PATH}/guild.js'></script>"
  end

  js_shun = ''
  if status >= 5
    js_shun << '<script src="https://d3js.org/d3.v5.min.js"></script>'
    js_shun << "<link href='#{$CSS_PATH}/c3.css' rel='stylesheet'>"
    js_shun << "<script type='text/javascript' src='#{$JS_PATH}/c3.min.js'></script>"
    js_shun << "<script type='text/javascript' src='#{$JS_PATH}/shun.js'></script>" 
  end

  js_master = ''
  if status >= 8
    js_master = "<script type='text/javascript' src='#{$JS_PATH}/master.js'></script>"
  end

  x_card = ''

  html = <<-"HTML"
<!DOCTYPE html>
<head>
  #{refresh}
  <title>栄養ブラウザ #{sub_title}</title>
  <meta charset="UTF-8">
  <meta name="keywords" content="栄養士,管理栄養士,無料,フリー,ダイエット,減量,Webサービス,食品成分表.献立,レシピ,検索,食事,評価,記録,栄養計算,栄養指導,フードインフォマティクス,インフォマティクス,食品情報解析,栄養情報解析,nutrition,Nutritionist,food,informatics,diet">
  <meta name="description" content="*栄養者の慾を如意自在に同化するユビキタス栄養ツール、栄養士、管理栄養士が活動に必要な食品成分の閲覧、料理の栄養計算、レシピの管理などが無料できる">
  <meta name="robots" content="index,follow">
  <meta name="author" content="ばきゅら京都Lab">

  <!-- Twitter card -->
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:site" content="@ho_meow" />
  <meta name="twitter:title" content="栄養ブラウザ" />
  <meta name="twitter:description" content="栄養者のユビキタスツール" />
  <meta name='twitter:image' content='https://bacura.jp/nb/#{$PHOTO}/nb.png' />
  <meta name="twitter:image:alt" content="栄養ブラウザロゴ" />

  <!-- Jquery -->
  #{$JQUERY}
  <!-- <script type="text/javascript" src="./jquery-3.6.0.min.js"></script> -->

  <!-- bootstrap -->
  #{$BS_CSS}
  #{$BS_JS}
  <!-- <link rel="stylesheet" href="bootstrap-dist/css/bootstrap.min.css"> -->
  <!-- <script type="text/javascript" src="bootstrap-dist/js/bootstrap.min.js"></script> -->

  <link rel="stylesheet" href="#{$CSS_PATH}/core.css">
  <script type="text/javascript" src="#{$JS_PATH}/core.js"></script>
  #{js_guild}
  #{js_shun}
  #{js_master}

  #{tracking}
</head>

<body class="body" id='top' onContextmenu='return false;'>
  <span class="world_frame" id="world_frame">
HTML

  puts html
end

#==============================================================================
# HTML footer
#==============================================================================
def html_foot()
    banner = "<a href='https://bacura.jp'><img src='https://bacura.jp/nb/#{$PHOTO}/BKL_banner_h125.png' alt='ばきゅら京都Lab'></a>"
    html = <<-"HTML"
      <div align='center' class='koyomi_today' onclick="window.location.href='#top';"><img src='bootstrap-dist/icons/geo.svg' style='height:2em; width:2em;'></div>
      <br>
      <footer class="footer">
        <div align="center">
          #{banner}
        </div>
      </footer>
    </span>
  </body>
</html>
HTML

  puts html
end


#==============================================================================
# HTML Tracking & adsense code
#==============================================================================
def tracking()
  code = <<-"CODE"
<script src="//accaii.com/bacura/script.js" async></script><noscript><img src="//accaii.com/bacura/script?guid=on"></noscript>

<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-HKNQHH8RH9"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-HKNQHH8RH9');
</script>

CODE

  return code
end

def adsense_info()
  code = <<-"CODE"
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4873824995474205"
     crossorigin="anonymous"></script>
<!-- 栄養ブラウザ表紙 -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4873824995474205"
     data-ad-slot="9558272424"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>


CODE

  return code
end

def adsense_printv()
  code = <<-"CODE"
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4873824995474205"
     crossorigin="anonymous"></script>
<!-- レシピ横 -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4873824995474205"
     data-ad-slot="2795355273"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>


CODE

  return code
end


#==============================================================================
# HTML Title page
#==============================================================================
def html_title()
  html = <<-"HTML"

<div class="container-fluid">
  <div class="row">
    <div class="col-6">

      栄養ブラウザは栄養士・管理栄養士活動を支援するためのツールを提供するWebサービス群です。<br>
      無料で食品成分の閲覧、料理の栄養計算、レシピの管理などが出来ます。<br>
      大半の機能はユーザーごとに機能しますので、是非ユーザー登録して使ってみて下さい。<br>
      下記のゲストアカウントを使えばお試しで登録後の状態を体験できます。<br>
      <br>

      <h4>お知らせ (20241012)</h4>
      <ul>
        <li>公開レシピが1221品になりました。</li>
        <br>
        <li>利用規定を一部変更しました。</li>
        <li>3Dレシピ検索機能を実装しました。</li>
        <li>パラレル食品機能を実装しました。</li>
        <li>幽体アカウントを実装しました。</li>
        <li>食品成分データを2021年12月27日版に更新しました。</li>
        <li>日本人の食事摂取基準を2020年に更新しました。</li>
      </ul>
      <hr>

      <h4>既知のバグ・障害・機能しないもの</h4>
      <ul>
        <li>マニュアルは作りかけです。</li>
        <li>レシピ帳の絞り込みがなんか怪しい。</li>
        <li>ギルメン旬の機能は基本まともに動きません。</li>
        <li>DB関連機能を逐次更新中につき、微妙に不安定さが増しています。</li>
      </ul>
      <hr>

      <h4>利用環境</h4>
      <ul>
        <li>食品成分表ブラウザはインターネットへの接続が必須で、HTML5に対応したWebブラウザの使用を推奨します。</li>
        <li>Javascript機能とCookie機能を使用していますので、どちらも有効にしてください。</li>
        <li>Windows11でVivaldi、EdgeとAndroidのGoogle chromeで動作確認しています。</li>
        <li>PCとタブレットでの利用を想定しています。スマホは細かすぎて見づらいと思います。</li>
      </ul>
      <hr>

      <h4>ゲストアカウントについて</h4>
      <ul>
        <li>IDに"guest"、"guest2"、"guest3"、パスワード無しでゲストアカウントでログインできます。</li>
        <li>複数ユーザーが同時に使用すると、勝手に設定の変更やログアウトが発生します。</li>
        <li>予告なしで設定や保存内容が初期化されます。</li>
        <li>気に入ったらアカウントの<a href="regist.cgi">登録</a>をお願いします。</li>
      </ul>
      <hr>

      <h4>使用データ</h4>
      <ul>
        <li>栄養ブラウザで使用する食品成分データは、文部科学省が公開している「日本食品標準成分表2020年版（八訂）増補2023年」を使用しています。</li>
        <li>データ中の()、Tr、-記号なども同様の意味で用いられています。また、当サイトで得たデータの使用については文部科学省の方針に従ってください。</li>
        <li>一部の食品の区分や名称は元データがカオスなので、独自に変更を加えています。</li>
        <li>詳しくは、<a href="http://www.mext.go.jp/a_menu/syokuhinseibun/index.htm">文部科学省　日本食品標準成分表・資源に関する取組</a>をご覧下さい。</li>
        <li>一部の食品重量の単位変換は女子栄養大学出版部出版の「調理のためのベーシックデータ第4版、第6版」を参考にしています。</li>
      </ul>

      <h4>ローカルでの使用</h4>
      <ul>
        <li>栄養ブラウザは<a href='https://github.com/bacura/nb2020/'>Github</a>で全てのソースが公開されています。</li>
        <li>その気になればローカルでサービス自体を稼働させることが出来ますがインストーラー、ドキュメント類が整備されておりません。</li>
        <li>動かしてみたい人は吉山（ばきゅら京都Lab）info@bacura.jpまでご連絡ください。</li>
      </ul>


      <h4>利用規程</h4>
      <ol type="1" class="terms">
        <li>本サービスとはばきゅら京都Labにより運営されている「栄養ブラウザ」を指します。</li>
        <li>利用者とは本サービスを各自の端末から利用する者を指します。</li>
        <li>利用者は本サービスを本規約の定めに従って利用しなければなりません。</li>
        <li>本サービスに起因して利用者に生じたあらゆる損害について、ばきゅら京都Labは一切の責任を負いません。</li>
        <li>利用者はメールアドレス以外の一切の個人情報を本サービスに入力することを禁止します。</li>
        <li>利用者が本サービスに登録したデータは本サービスが自由に使用できるものとします。（でないと、保存したり表示させることが出来ません＞＜）</li>
        <li>本サービスの運用に支障を与えるあらゆる行為を禁止します。</li>
        <li>本利用規約は利用者に通知することなく変更できるものとします。</li>
      </ol>
    </div>

    <div class="col-6">
      [空き地]<br>
      #{adsense_info()}
    </div>

  </div>
</div>


HTML

  return html
end





#==============================================================================
# DATE & TIME
#==============================================================================
@time_now = Time.now
@datetime = @time_now.strftime( "%Y-%m-%d %H:%M:%S" )
@date = @time_now.strftime( "%Y-%m-%d" )


#==============================================================================
# MEDIA
#==============================================================================
$WM_FONT = 'さざなみゴシック'
