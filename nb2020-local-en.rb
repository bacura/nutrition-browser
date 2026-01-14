#Nutrition browser 2020 local English pack 0.3.3 (2026/01/07)

#==============================================================================
# STATIC
#==============================================================================
@title = 'Nutri browser'

@category = %w( Special Grains Tubers_Stearch Sugars_Sweeteners Legumes Nuts Seeds Vegetables Fruits Mushrooms Algae Seafood Meat Eggs Dairy Fats_Oils Confectionery Beverages Seasonings Processed_Foods Special )
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

@fct_name = {
'FG'=>'FoodGroup','FN'=>'FoodID','SID'=>'IndexID','Tagnames'=>'FoodName','REFUSE'=>'Refuse',
'ENERC'=>'Energy(kJ)','ENERC_KCAL'=>'Energy(kcal)','WATER'=>'Water',
'PROTCAA'=>'Protein_AA','PROT'=>'Protein','PROTV'=>'Protein*',
'FAT'=>'Fat','FATNLEA'=>'TAG_eq','FATV'=>'Fat*',
'FASAT'=>'SFA','FAMS'=>'MUFA','FAPU'=>'PUFA',
'FAPUN3'=>'PUFA_n3','FAPUN6'=>'PUFA_n6','CHOLE'=>'Cholesterol',
'CHOCDF'=>'Carbohydrate','CHOAVLM'=>'Available_CHO_MonoEq','CHOAVL'=>'Available_CHO','CHOAVLDF'=>'Available_CHO_Diff','CHOV'=>'Carbohydrate*',
'FIB'=>'DietaryFiber','FIBTG'=>'TotalFiber_P','FIBSOL'=>'SolubleFiber_P','FIBINS'=>'InsolubleFiber_P',
'FIBTDF'=>'TotalFiber_A','FIBSDFS'=>'LowMW_SolFiber_A','FIBSDFP'=>'HighMW_SolFiber_A','FIBIDF'=>'InsolubleFiber_A',
'STARES'=>'ResistantStarch','POLYL'=>'SugarAlcohol','ASH'=>'Ash',
'NA'=>'Na','K'=>'K','CA'=>'Ca','MG'=>'Mg','P'=>'P','FE'=>'Fe','ZN'=>'Zn','CU'=>'Cu','MN'=>'Mn',
'ID'=>'I','SE'=>'Se','CR'=>'Cr','MO'=>'Mo',
'RETOL'=>'Retinol','CARTA'=>'AlphaCarotene','CARTB'=>'BetaCarotene','CRYPXB'=>'BetaCryptoxanthin',
'CARTBEQ'=>'BetaCaroteneEq','VITA_RAE'=>'RAE','VITD'=>'VitD',
'TOCPHA'=>'AlphaTocopherol','TOCPHB'=>'BetaTocopherol','TOCPHG'=>'GammaTocopherol','TOCPHD'=>'DeltaTocopherol',
'VITK'=>'VitK','THIA'=>'VitB1','RIBF'=>'VitB2','NIA'=>'Niacin','NE'=>'NiacinEq',
'VITB6A'=>'VitB6','VITB12'=>'VitB12','FOL'=>'Folate','PANTAC'=>'PantothenicAcid','BIOT'=>'Biotin','VITC'=>'VitC',
'OA'=>'OrganicAcid','ALC'=>'Alcohol','NACL_EQ'=>'SaltEq','Notice'=>'Notes'
}

@palette_default_name = %w( Simple Basic5 Basic12 Basic21 All )
$PALETTE_DEFAULT_NAME = @palette_default_name
@palette_default = %w( 00000010001001000000000010000000000000000000000000000000000000000000000001 00000010001001000000000010000000000000000000000000000000000000000000000001 00000010001001000000000011000000000001100100000000000001000001100000000001 00000010001001000000000011000000000001110111000000000001000001101111001011 00001111111111111111111111111111111111111111111111111111111111111111111111 )
$PALETTE_DEFAULT = @palette_default
@palette_bit_all = [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1 ]
$PALETTE_BIT_ALL = @palette_bit_all

@recipe_type = %w( Unset Japanese_Washoku Japanese_Yoshoku Chinese Italian French Ethnic Western Fusion )
@recipe_role = %w( Unset Staple_Main Main Side Soup Dessert Drink Seasoning BabyFood Base )
@recipe_tech = %w( Unset Boil_Simmer Grill_StirFry Steam Fry Mix Raw Chill Oven Microwave )
@recipe_time = %w( Unset <=5min <=10min <=15min <=20min <=30min <=45min <=60min <=120min >=121min )
@recipe_cost = %w( Unset <=50yen <=100yen <=150yen <=200yen <=300yen <=400yen <=500yen <=600yen <=800yen >=1000yen )

@sub_group = %w( '' GreenYellowVeg Milk Miso SoySauce Salt )

@account = %w( Withdraw General RegularGuild guest CuteGuild SeasonalGuild Daughter Astral SubMaster GuildMaster )

@kex_std = {
'Height'=>'cm','Weight'=>'kg','BMI'=>'','BodyFat'=>'%','Waist'=>'cm','BristolScale'=>'',
'Steps'=>'steps','METs'=>'','DeltaEnergy'=>'kcal','SBP'=>'mmHg','DBP'=>'mmHg',
'FPG'=>'mg/dl','HbA1c'=>'%','TG'=>'mg/dL','TC'=>'mg/dL','LDL'=>'mg/dL','HDL'=>'mg/dL','UA'=>'mg/dL',
'AST'=>'IU/L','ALT'=>'IU/L','ALP'=>'IU/L','LDH'=>'IU/L','GGT'=>'IU/L'
}

@kex_presets['BodyManagement'] =
'{"kexu":{"Weight":"kg","BodyFat":"%","DeltaEnergy":"kcal"},"kexa":{"Weight":"1","BodyFat":"1","DeltaEnergy":"1"},"kexg":{},"kexup":{},"kexbtm":{}}'

@something = {
'?--'=>'Ate_Small','?-'=>'Ate_Light','?='=>'Ate_Normal','?+'=>'Ate_Large','?++'=>'Ate_XL',
'?0'=>'NoMeal','?P'=>'PhotoOnly'
}

#==============================================================================
# HTML header
#==============================================================================
def html_head( interrupt, status, sub_title )
  refresh = ''
  refresh = '<meta http-equiv="refresh" content="0; url=index.cgi">' if interrupt == 'refresh'

  js_guild = ''
  if status >= 1
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
  <title>Nutrition browser #{sub_title}</title>
  <meta charset="UTF-8">
<!--
	<meta name="keywords" content="Nutritionist, Registered Dietitian, Dietitian, Free Nutrition Tools, Diet, Weight Loss, Healthy Eating, Meal Planning, Recipes, Food Database, Food Composition Table, Nutrition Calculator, Nutrition Tracking, Nutrition Analysis, Nutrition Counseling, Dietary Assessment, Food Informatics, Nutrition Informatics, Food Information Analysis, Web Service, Online Nutrition Tool">
	<meta name="description" content="A free, ubiquitous nutrition tool that adapts to your needs. Nutritionists and registered dietitians can browse food composition data, calculate recipe nutrition, and manage recipes easily online.">
	<meta name="robots" content="index,nofollow"> -->
-->
  <meta name="robots" content="noindex,nofollow">
  <meta name="author" content="Bacura KYOTO Lab">

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
    banner = "<a href='https://bacura.jp'><img src='#{$PHOTO}/BKL_banner_h125.png' alt='Lab'></a>"
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

CODE

  return code
end

def adsense_info()
  code = <<-"CODE"

CODE

  return code
end

def adsense_printv()
  code = <<-"CODE"

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
    This is a highly unstable public beta version of the Nutrition Browser.<br>
    <a href="https://eiyo-b.com/">Click here to access the official Nutrition Browser</a><br>
    </div>

    <div class="col-6">
      [Ad Space]<br>
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
