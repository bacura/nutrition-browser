#Nutrition browser 2020 brain 0.6.10 (2026/01/25)

#==============================================================================
# LIBRARY
#==============================================================================
require 'bigdecimal'
#require 'nkf'

#==============================================================================
#STATIC
#==============================================================================


#==============================================================================
#DEFINITION
#==============================================================================


#### R用データベース処理
def mdbr( query, html_opt, debug )
  begin
    db = Mysql2::Client.new(:host => "#{$HOST}", :username => "#{$USERR}", :password => "", :database => "#{$DBR}", :encoding => "utf8" )
    t = query.chop
    query_ = ''
    query_ = query if debug
    if /\;/ =~ t
        puts "<span class='error'>[mdbr]ERROR!! #{query_}</span><br>"
        exit( 9 )
    end
    res = db.query( query )
    db.close
  rescue
    if html_opt
      html_init( nil )
      html_head( nil )
    end
      puts "<span class='error'>[mdbr]ERROR!!<br>"
      puts "#{query_}</span><br>"
  end
  return res
end


#### RRトークン発行
def issue_token()
  token = SecureRandom.base64(16)

  return token
end


#### 食品重量の決定
def food_weight_check( food_weight )
  fw = food_weight
  fw = '100' if fw == nil || fw == '' || fw == '0'
  fw.tr!( "０-９", "0-9" ) if /[０-９]/ =~ fw
  fw.gsub!(/[．、。，,]/, '.')
  fw.gsub!(/[／]/, '/')
  fw.gsub!(/[＋]/, '+')
  fw.gsub!(/[ー]/, '-')
  uv = BigDecimal( '0' )

  begin
    # 分数処理
    if /\d+\+\d+\/\d+/ =~ fw
      # 帯分数
      a = fw.scan( /(\d+)\+\d+\/\d+/ )[0][0].to_i
      b = fw.scan( /\d+\+(\d+)\/\d+/ )[0][0].to_i
      c = fw.scan( /\d+\+\d+\/(\d+)/ )[0][0].to_i
      if c == 0
        fw = 100
        uv = 100
      else
        uv = BigDecimal( b ) / c + a
      end
    elsif /\d+\/\d+/ =~ fw
      # 仮分数
      b = fw.scan( /(\d+)\/\d+/ )[0][0].to_i
      c = fw.scan( /\d+\/(\d+)/ )[0][0].to_i
      if c == 0
        fw = 100
        uv = 100
      else
        uv = BigDecimal( b ) / c
      end
    else
      uv = BigDecimal( fw )
    end
  rescue
    puts "<span class='error'>[food_weight_check]ERROR!!"
    puts "food_weight:#{food_weight}</span><br>"
    fw = 100
    uv = 100
  end

  return fw, uv
end


#### from unit volume to weight
def unit_weight( vol, uc, fn )
  w = 0.0

  res = $DB.prepare( "SELECT unit FROM #{$TB_EXT} WHERE FN=?" ).execute( fn )
  if res.first
    if res.first['unit'] != nil && res.first['unit'] != ''
      unith = JSON.parse( res.first['unit'] )
      begin
        w = ( BigDecimal( unith[uc].to_s ) * vol ).round( 1 )
      rescue
        puts "<span class='error'>[unit_weight]ERROR!!<br>"
        puts "vol:#{vol}<br>"
        puts "uc:#{uc}<br>"
        puts "fn:#{fn}</span><br>"
      end
    end
  end

  return w
end


#### 食品番号と一皿分の重さを抽出
#sumはデコード前のsum
#dishはsumが何皿分を示す数値
#ew_modeは0->通常重量、1->予想重量
def extract_sum( sum, dish, ew_mode )
  foods = sum.split( "\t" )
  fns = []
  fws = []
  tw = 0
  foods.each do |e|
    t = e.split( ':' )
    fns << t[0]
    if t[0] == '-' || t[0] == '+'
      fws << 0
    elsif ew_mode == 1 && t[7] != nil && t[7] != ''
      fws << ( BigDecimal( t[7] ) / dish.to_i ).floor( 2 )
      tw += ( BigDecimal( t[7] ) / dish.to_i ).floor( 2 )
    else
      fws << ( BigDecimal( t[1] ) / dish.to_i ).floor( 2 )
      tw += ( BigDecimal( t[1] ) / dish.to_i ).floor( 2 )
    end
  end

  return fns, fws, tw
end


def menu2rc( user, code )
  codes = []
  res = $DB.prepare( "SELECT meal FROM #{$TB_MENU} WHERE user=? AND code=?" ).execute( user.name, code )
  if res.first
    codes = res.first['meal'].split( "\t" ) unless res.first['meal'].to_s.empty?
  end

  return codes
end


def recipe2fns( user, code, rate, unit, ew_mode )
  ew_mode ||= 0
  fns, fws, tw = [], [], []

  res = $DB.prepare( "SELECT sum, dish FROM #{$TB_RECIPE} WHERE user=? AND code=?" ).execute( user.name, code )
  if res.first
    fns, fws, tw = extract_sum( res.first['sum'], res.first['dish'], ew_mode )

    if unit == '%'
      fws.map! do |x| x * rate / 100 if x != '-' && x != '+' end

    elsif unit == 'kcal'
      rr = $DB.prepare( "SELECT ENERC_KCAL FROM #{$TB_FCZ} WHERE user=? AND base = 'recipe' AND origin=?" ).execute( user.name, code )
      rate = ( rate / BigDecimal( rr.first['ENERC_KCAL'] ))
      fws.map! do |x| x * rate if x != '-' && x != '+' end

    else
      fws.map! do |x| x * rate / tw if x != '-' && x != '+' end

    end
  end

  return fns, fws, tw
end


#### 特殊単位数変換
def unit_value( iv )
  if iv >= 10
    iv.to_i
  elsif iv >= 1
    iv == iv.to_i ? iv.to_i : iv.to_f
  else
    iv.to_f
  end
end


#Extra liberally for plot
def exlib_plot()
  puts '<link rel="stylesheet" href="c3/c3.min.css">'
  puts '<script type="text/javascript" src="d3/d3.min.js"></script>'
  puts '<script type="text/javascript" src="c3/c3.min.js"></script>'
end

#==============================================================================
# CLASS
#==============================================================================

class Palette
  attr_accessor :sets, :bit

  def initialize( user )
    @user = user
    @sets = Hash.new
    @bit = []

    if @user.name
      res = $DB.prepare( "SELECT * FROM #{$TB_PALETTE} WHERE user=?" ).execute( @user.name )
      if res.first
        res.each do |e| @sets[e['name']] = e['palette'] end
      else
        $PALETTE_DEFAULT.each.with_index do |e, i|
          $DB.prepare( "INSERT INTO #{$TB_PALETTE} SET user=?, name=?, palette=?" ).execute( @user.name, $PALETTE_DEFAULT_NAME[i], e )
          @sets[$PALETTE_DEFAULT_NAME[i]] = e
        end
      end

    else
      $PALETTE_DEFAULT_NAME[$DEFAULT_LP].each.with_index do |e, i|
        @sets[e] = $PALETTE_DEFAULT[$DEFAULT_LP][i]
      end
    end
  end

  def set_bit( palette )
    palette = $PALETTE_DEFAULT_NAME[$DEFAULT_LP][1] if palette.to_s.empty?
    @bit = @sets[palette].split( '' )
    @bit.map! do |x| x.to_i end
  end
end


class FCT
  attr_accessor :items, :names, :units, :frcts, :solid, :total, :fns, :foods, :foods_, :weights, :refuses, :total_weight, :zname

  def initialize( user, item_, name_, unit_, frct_, frct_accu = 1, frct_mode = 0 )
    @user = user
    @item = item_
    @name = name_
    @unit = unit_
    @frct = frct_
    @items = []
    @names = []
    @units = []
    @frcts = []
    @fns = []
    @foods = []
    @foods_ = []
    @weights = []
    @refuses = []
    @solid = []
    @total = []
    @total_weight = BigDecimal( '0' )
    @frct_accu = frct_accu
#    @frct_accu = 1 if @frct_accu == nil
    @frct_mode = frct_mode
#    @frct_mode = 0 if @frct_mode == nil
  end

  def load_palette( palette )
    @items = []
    @names = []
    @units = []
    @frcts = []
    @item.each.with_index do |e, i|
      if palette[i] == 1 && e != 'REFUSE'
        @items << e
        @names << @name[e]
        @units << @unit[e]
        @frcts << @frct[e]
      end
    end
  end

  def set_food( food_no, food_weight, non_food )
    c = 0
    food_no.each do |e|
      if e == '-'
        if non_food
          @fns << '-'
          @solid << '-'
          @foods << '-'
          @weights << '-'
          @refuses << '-'
        end
      elsif e == '+'
        if non_food
          @fns << '+'
          @solid << '+'
          @foods << '+'
          @weights << '+'
          @refuses << '+'
        end
      elsif e == '00000'
        if non_food
          @fns << '0'
          @solid << '0'
          @foods << ''
          @weights << '0'
          @refuses << '0'
        end
      else
        if /U/ =~ e && @user.name != nil
          q = "SELECT * from #{$TB_FCTP} WHERE FN='#{e}' AND user='#{@user.name}';"
          q = "SELECT * from #{$TB_FCTP} WHERE FN='#{e}';" if @user.name == '+anonymous+'
          qq = "SELECT * from #{$TB_TAG} WHERE FN='#{e}' AND user='#{@user.name}';"
        elsif /P/ =~ e
          q = "SELECT * from #{$TB_FCTP} WHERE FN='#{e}';"
          qq = "SELECT * from #{$TB_TAG} WHERE FN='#{e}';"
        else
          q = "SELECT * from #{$TB_FCT} WHERE FN='#{e}';"
          qq = "SELECT * from #{$TB_TAG} WHERE FN='#{e}';"
        end
        res = $DB.query( q )&.first
        if res

          @fns << e
          a = []
          @items.each do |ee|
            if ee != 'REFUSE'
              a << res[ee]
            else
              @refuses << res[ee]
            end
          end

          @solid << Marshal.load( Marshal.dump( a ))
          res2 = $DB.query( qq )&.first
          if res2
            @foods << tagnames( res2 )
            @foods_ << res2['name']
            @weights << food_weight[c]
          end
        else
          c -= 1
        end
      end
      c += 1
    end
  end

  def calc()
    @total = []
    @items.size.times do |c| @total << BigDecimal( 0 ) end
    @total_weight = 0.0
    @foods.size.times do |f|
      @items.size.times do |i|
        if @weights[f] == 0
          @solid[f][i] = 0
        else
          t = @solid[f][i]
          t = 0 if t == nil
          t.to_s.sub!( '(', '' )
          t.to_s.sub!( ')', '' )
          t = 0 if t == 'Tr'
          t = 0 if t == '-'
          t = 0 if t == ''
          t = 0 if t == '*'
          t = ( BigDecimal( t.to_s ) * @weights[f] / 100 )

          if @frct_accu == 0
            case @frct_mode.to_i
            when 0, 1  # 四捨五入
              t = t.round( @frcts[i] )
            when 2  # 切り上げ
              t = t.ceil( @frcts[i] )
            when 3  # 切り捨て
              t = t.floor( @frcts[i] )
            end
          end
          @solid[f][i] = t
          @total[i] += t
        end
      end
      @total_weight += @weights[f]
    end
  end

  def digit()
    @foods.size.times do |f|
      @items.size.times do |i|
        if @frct_accu == 1
          case @frct_mode.to_i
          when 2  # 切り上げ
            @solid[f][i] = @solid[f][i].ceil( @frcts[i] )
          when 3  # 切り捨て
            @solid[f][i] = @solid[f][i].floor( @frcts[i] )
          else  # 四捨五入
            @solid[f][i] = @solid[f][i].round( @frcts[i] )
          end
        end

        if @frcts[i] == 0
          @solid[f][i] = @solid[f][i].to_i
        else
          @solid[f][i] = @solid[f][i].to_f
        end
      end
    end

    @items.size.times do |i|
      case @frct_mode.to_i
      when 2  # 切り上げ
        @total[i] = @total[i].ceil( @frcts[i] )
      when 3  # 切り捨て
        @total[i] = @total[i].floor( @frcts[i] )
      else
        @total[i] = @total[i].round( @frcts[i] )
      end

      if @frcts[i] == 0
        @total[i] = @total[i].to_i
      else
        @total[i] = @total[i].to_f
      end
    end
  end

  def singlet()
    @total = []
    @total_weight = @weights[0]
    @items.size.times do |i| @total[i] = BigDecimal( @solid[0][i].to_s ) end
  end

  def gramt( g )
    @items.size.times do |i|
      @total[i] = @total[i] / @total_weight * g
    end
  end

  def pickt( item )
    item_index = @items.index( item )
    if item_index
      return @total[item_index]
    else
      return nil
    end
  end

  def calc_pfc()
    ei = @items.index( 'ENERC_KCAL' )
    pi = @items.index( 'PROTV' )
    fi = @items.index( 'FATV' )
    pfc = []
    if ei != nil
      pfc[0] = ( @total[pi] * 4 / @total[ei] * 100 ).round( 1 )
      pfc[1] = ( @total[fi] * 4 / @total[ei] * 100 ).round( 1 )
      pfc[2] = ( 100 - pfc[0] - pfc[1] ).round( 1 )
    end

    return pfc
  end

  def into_solid( fct )
    @fns << nil
    @foods << nil
    @weights << 100
    @solid << Marshal.load( Marshal.dump( fct ))
  end

  def into_zero()
    @fns << nil
    @foods << nil
    @weights << 100
    zero = []
    @item.size.times do zero << 0 end
    @solid << Marshal.load( Marshal.dump( zero ))
  end

  def put_solid( item, solid_no, value )
    item_index = @items.index( item )
    if item_index
      @solid[solid_no][item_index] = value

      return true
    else
      return false
    end
  end

  def load_fcz( base = nil, fzcode = nil )
    return false if fzcode.to_s == ''

    r = $DB.prepare( "SELECT * FROM #{$TB_FCZ} WHERE user=? AND code=? AND base=?" ).execute( @user.name, fzcode, base )
    if r.first
      a = []
      @zname = r.first['name']
      @items.each do |e|
        t = r.first[e]
        t = 0 if t == nil || t == ''
        a << BigDecimal( t )
      end
      @solid << Marshal.load( Marshal.dump( a ))
      @fns << fzcode
      @foods << base
      @weights << 100

      return true
    else
      puts "<span class='error'>FCZ load ERROR[#{fzcode}]</span>"
      return false
    end
  end

  def delete_fcz( base = nil, fzcode = nil, origin = nil )
    if !base.nil? && !fzcode.nil? 
      $DB.prepare( "DELETE FROM #{$TB_FCZ} WHERE user=? AND code=? AND base=?" ).execute( @user.name, fzcode, base ) unless @user.barrier
    elsif !base.nil? && !origin.nil? 
      $DB.prepare( "DELETE FROM #{$TB_FCZ} WHERE user=? AND origin=? AND base=?" ).execute( @user.name, origin, base ) unless @user.barrier
    elsif !base.nil?
      $DB.prepare( "DELETE FROM #{$TB_FCZ} WHERE user=? AND base=?" ).execute( @user.name, base ) unless @user.barrier
    end
  end

  def load_fctp( code )
    if /^P/ =~ code
      r = $DB.prepare( "SELECT * FROM #{$TB_FCTP} WHERE FN=?" ).execute( code )
    else
      r = $DB.prepare( "SELECT * FROM #{$TB_FCTP} WHERE FN=? AND user=?" ).execute( code, @user.name )
    end

    if r.first
      a = []
      @items.each do |e|
        t = r.first[e]
        t = 0 if t == nil || t == '' || t == '-'
        a << BigDecimal( t )
      end
      @solid << Marshal.load( Marshal.dump( a ))
      @fns << code
      @foods << 'fctp'
      @weights << 100

      return r.first['REFUSE'], r.first['Notice']
    else
      puts "<span class='error'>fctp load ERROR[#{code}]</span>"
      return nil, nil
    end
  end

  def load_cgi( cgi )
    a = []
    @items.each do |e|
      t = cgi[e]
      t = 0 if t == '' || t == nil || /[^0-9\-\.]/ =~ t
      a << BigDecimal( t )
    end
    @solid << Marshal.load( Marshal.dump( a ))
    @fns << cgi['food_code']
    @foods << cgi['food_name']
    t = cgi['food_weight']
    t = '100' if t == '' || t == nil || /[^0-9\-\.]/ =~ t
    @weights << BigDecimal( t )
  end

  def save_fcz( zname, base, origin )
    fct_ = ''
    @items.size.times do |i| fct_ << "#{@items[i]}='#{@total[i]}'," end
    fct_ << " weightp='#{@total_weight}'"

    code = ''
    r = $DB.prepare( "SELECT code FROM #{$TB_FCZ} WHERE user=? AND origin=? AND base=?" ).execute( @user.name, origin, base )
    if r.first
      $DB.query( "UPDATE #{$TB_FCZ} SET #{fct_} WHERE user='#{@user.name}' AND origin='#{origin}' AND base='#{base}';" )
      code = r.first['code']
    else
      code = generate_code( @user.name, 'z' )
      $DB.query( "INSERT INTO #{$TB_FCZ} SET code='#{code}', base='#{base}', name='#{zname}', user='#{@user.name}', origin='#{origin}', #{fct_};" )
    end

    return code
  end

  def sql()
    sql = ''
      @items.size.times do |i| sql << "#{@items[i]}='#{@total[i]}'," end
      sql.chop!

      return sql
  end

  def flash()
    @fns = []
    @foods = []
    @weights = []
    @refuses = []
    @solid = []
    @total = []
    @total_weight = BigDecimal( '0' )
  end

  def debug()
    p @fns
    p @foods
    p @weights
    p @refuses
    p @solid
    p @total
    p @total_weight
    p @frct_accu
    p @frct_mode

  end
end


class FCZ
  attr_accessor :res

  def initialize( user, base = nil, code = nil )
    @code = code
    @origin = nil
    @base = base
    @name = nil
    @user = user
    @date = nil
    @res = nil
  end

  def set_code( code )
    @code = code
  end

  def load_db( code = nil )
    @code = code unless code.nil?
    @res = $DP.prepare( "SELECT * FROM #{$TB_FCZ} WHERE user=? AND base=? AND code=?" ).execute( @user.name, @base, @code )&.first
    if @res
      @origin = @res['origin']
      @name = @res['name']
      @date = @res['date']
    end

    return @res
  end

  def load_off_lim_db( offset, limit )
    @res = $DP.prepare( "SELECT * FROM #{$TB_FCZ} WHERE user=? AND base=? ORDER BY name LIMIT ?, ?" ).execute( @user.name, @base, offset, limit )&.first

    return @res
  end

  def count_db()
    @res = $DB.prepare( "SELECT COUNT(code) FROM #{$TB_FCZ} WHERE user=? AND base=?" ).execute( @user.name, @base )&.first

    return @res['COUNT(code)'].to_i
  end

  def delete( code = nil )
    @code = code unless code.nil?
    $DP.prepare( "DELETE FROM #{$TB_FCZ} WHERE user=? AND base=? AND code=?" ).execute( @user.name, @base, @code ) unless @user.barrier
    @code = nil
    @origin = nil
    @name = nil
    @date = nil

  end
end


class Memory
  attr_accessor :code, :user, :category, :pointer, :content, :date

  def initialize( user )
    @user = user
    @code = nil
    @category = nil
    @pointer = nil
    @content = nil
    @date = nil
    @public = 0
    @public = 1 if @user.status >= 8

  end

  def get_categories()
    array = []
    res = $DB.query( "SELECT DISTINCT category FROM #{$TB_MEMORY};" )
    res.each do |e| array << e['category'] end

    return array
  end

  def get_pointers( category = nil )
    array = []
    sql_where = category.nil? ? '' : " WHERE category='#{category}'"
    res = $DB.query( "SELECT DISTINCT pointer FROM #{$TB_MEMORY}#{sql_where};" )
    res.each do |e| array << e['pointer'] end

    return array
  end


  def load_db()
    res = $DB.prepare( "SELECT * FROM #{$TB_MEMORY} WHERE code=?" ).execute( @code )
    if res.first
      @category = res.first['category']
      @pointer = res.first['pointer']
      @content = res.first['content']

      return true

    else
      puts "<span class='error'>[Memory load]ERROR!!<br>"
      puts "code:#{@code}</span><br>"

      return false
    end
  end

  def save_db()
    unless @code == nil
      res = $DB.prepare( "SELECT code FROM #{$TB_MEMORY} WHERE code=?" ).execute( @code )
      if res.first
        $DB.prepare( "UPDATE #{$TB_MEMORY} SET category=?, pointer=?, content=?, date=? WHERE code=?" ).execute( @category, @pointer, @content, @date, @code )
      else
        $DB.prepare( "INSERT INTO #{$TB_MEMORY} SET code=?, user=?, category=?, pointer=?, content=?, date=?, public=?" ).execute( @code, @user.name, @category, @pointer, @content, @date, @public )
      end
    else
      puts "<span class='worning'>[Memory get_pointers]WORNING!!<br>"
      puts "No code</span><br>"
    end
  end

  def delete_db()
    unless @code == nil
      user_sql = @user.status >= 8 ? '' : "AND user=?"
      query = "DELETE FROM #{$TB_MEMORY} WHERE code=? #{user_sql};"
      $DB.prepare( query ).execute( @code, @user.name )
    else
      puts "<span class='worning'>[Memory delete_db]WORNING!!<br>"
      puts "No code</span><br>"
    end
   end

  def delete_category()
    if @user.status >= 8
      $DB.prepare( "DELETE FROM #{$TB_MEMORY} WHERE category=?" ).execute( @category )
    end
  end

  def change_category( new_category )
    if @user.status >= 8
      unless new_category == nil
        $DB.prepare( "UPDATE #{$TB_MEMORY} SET category=? WHERE category=?" ).execute( new_category, @category )
      else
        puts "<span class='worning'>[Memory change_category]WORNING!!<br>"
        puts "No new_category</span><br>"
      end
    end
  end

  def get_solid( range )
    solid = []

    unless @category == nil
      sql_user = "AND user='#{@user.name}'"
      sql_user = '' if @user.status >= 8

      res = $DB.query( "SELECT user, code, pointer, content FROM #{$TB_MEMORY} WHERE category='#{@category}' #{sql_user} ORDER BY pointer;" )
      res.each do |e| solid << e end 
    else
      sql_user = ''
      sql_user = "AND user='#{@user.name}'" if range == 'user'
      sql_user = "AND public='1'" if range == 'public'
      sql_user = "AND ( user='#{@user.name}' OR public='1' )" if range == 'merge'

      res = $DB.query( "SELECT * from #{$TB_MEMORY} WHERE pointer='#{@pointer}' #{sql_user};" )
      res.each do |e| solid << e end 
    end

    return solid
  end

  def load_cgi( cgi )
    @code = cgi['code'].to_s
    @category = cgi['category'].to_s
    @pointer = cgi['pointer'].to_s
    @content = cgi['content'].to_s
  end
end


class Koyomi
  attr_accessor :user, :start_day, :end_day, :solid, :fz_bit, :fz_code, :updates

  def initialize( user )
    @user = user
    @start_day = nil
    @end_day = nil
    @solid = Hash.new
    @fz_bit = Hash.new
    @fz_code = Hash.new
    @updates = []
  end

  def load_db( start_day, end_day = nil )
    @start_day = start_day
    @end_day = end_day ? end_day : start_day
    @solid = {}
    @fz_bit = {}
    @fz_code = {}
    res = $DB.prepare( "SELECT * FROM #{$TB_KOYOMI} WHERE user=? AND koyomi!='' AND koyomi IS NOT NULL AND date BETWEEN ? AND ? ORDER BY date;" ).execute( @user.name, @start_day, @end_day )
    if res.first
      res.each do |e|
        key = e['date'].to_s
        @solid[key] ||= ['', '', '', '', '']
        @fz_bit[key] ||= [0, 0, 0, 0, 0]
        @fz_code[key] ||= ['', '', '', '', '']

        @solid[key][e['tdiv'].to_i] = e['koyomi'].to_s
        @fz_bit[key][e['tdiv'].to_i] = e['freeze'].to_i
        @fz_code[key][e['tdiv'].to_i] = e['fzcode'].to_s
      end
      return true
    else
      return false
    end
  end

  def save_db()
    return if @user.barrier
    @updates.uniq.each do |key|
      5.times do |tdiv|
        next if @solid[key][tdiv].nil?
        res = $DB.query( "SELECT 1 FROM #{$TB_KOYOMI} WHERE user='#{@user.name}' AND date='#{key}' AND tdiv='#{tdiv}';" )
        if res.first
          $DB.query( "UPDATE #{$TB_KOYOMI} SET koyomi='#{@solid[key][tdiv]}', freeze='#{@fz_bit[key][tdiv]}', fzcode='#{@fz_code[key][tdiv]}' WHERE user='#{@user.name}' AND date='#{key}' AND tdiv='#{tdiv}';" )
        else
          next if @solid[key][tdiv].to_s.empty?
          $DB.query( "INSERT INTO #{$TB_KOYOMI} SET  koyomi='#{@solid[key][tdiv]}', freeze='#{@fz_bit[key][tdiv]}', fzcode='#{@fz_code[key][tdiv]}', user='#{@user.name}', date='#{key}', tdiv='#{tdiv}';" )
        end
      end
    end
    @updates = []
  end

  def add( ymd, tdiv, koyomi )
    if tdiv.to_i >= 0 && tdiv.to_i < 5
      @solid[ymd] ||= ['', '', '', '', '']
      @fz_bit[ymd] ||= [0, 0, 0, 0, 0]
      @fz_code[ymd] ||= ['', '', '', '', '']

      @solid[ymd][tdiv] = koyomi
      @fz_bit[ymd][tdiv] = 0
      @fz_code[ymd][tdiv] = ''
      @updates << ymd
    end
  end

  def add_sub( ymd, tdiv, koyomi_sub )
    if tdiv.to_i >= 0 && tdiv.to_i < 5
      @solid[ymd] ||= ['', '', '', '', '']
      @fz_bit[ymd] ||= [0, 0, 0, 0, 0]
      @fz_code[ymd] ||= ['', '', '', '', '']

      if @solid[ymd][tdiv] == ''
        @solid[ymd][tdiv] = koyomi_sub
      else
        @solid[ymd][tdiv] << "\t#{koyomi_sub}"
      end
      @updates << ymd
    end
  end

  def modify( ymd, tdiv, koyomi )
    if tdiv.to_i >= 0 && tdiv.to_i < 5
      @solid[ymd][tdiv] = koyomi
      @updates << ymd
    end
  end

  def get_sub( ymd, tdiv, order )
    if tdiv.to_i >= 0 && tdiv.to_i < 5 && @solid[ymd].to_s != ''
      koyomi_subs = @solid[ymd][tdiv].split( "\t" ) 
      koyomi_subs[order.to_i]
    else
      return nil
    end
  end

  def modify_sub( ymd, tdiv, order, koyomi_sub )
    if tdiv.to_i >= 0 && tdiv.to_i < 5
      koyomi_subs = @solid[ymd][tdiv].split( "\t" ) 
      if koyomi_sub == ''
        koyomi_subs.delete( order.to_i )
        @solid[ymd][tdiv] = '' if koyomi_subs.size == 0
      else
        koyomi_subs[order.to_i] = koyomi_sub
        @solid[ymd][tdiv] = koyomi_subs.join( "\t" )
      end
      @updates << ymd
    end
  end

  def clear( ymd, tdiv = 'all' )
    if tdiv.to_s == 'all'
      @solid[ymd] = ['', '', '', '', '']
      @fz_bit[ymd] = [0, 0, 0, 0, 0]
      @fz_code[ymd] = ['', '', '', '', '']
    elsif tdiv.to_i >= 0 && tdiv.to_i < 5
      @solid[ymd][tdiv] = ''
      @fz_bit[ymd][tdiv] = 0
      @fz_code[ymd][tdiv] = ''
    end
    @updates << ymd
  end

  def freeze( ymd, tdiv = 'all', freeze_bit )
      @fz_bit[ymd] ||= []
      if tdiv.to_s == 'all'
        5.times do |tdiv|
          @fz_bit[ymd][tdiv] = freeze_bit
        end
      elsif tdiv.to_i >= 0 &&  tdiv.to_i < 5
        @fz_bit[ymd][tdiv] = freeze_bit
      end
      @updates << ymd
  end

  def freeze_all( ymd, freeze_bit )
      @fz_bit[ymd] ||= []
      @fz_bit.each do |ymd,|
        5.times do |tdiv|
          @fz_bit[ymd][tdiv] = freeze_bit.to_i
        end
        @updates << ymd
      end
  end

  def freeze_flag( ymd, tdiv = 'all' )
    flag = false
    if tdiv == 'all'
      5.times do |tdiv|
        next if @fz_bit[ymd].nil?
        flag = true if @fz_bit[ymd][tdiv].to_i == 1
      end
    elsif tdiv.to_i >= 0 &&  tdiv.to_i < 5
        return flag if @fz_bit[ymd].nil?
        flag = true if @fz_bit[ymd][tdiv].to_i == 1
    end

    return flag
  end

  def delete_empty_db()
    $DB.query( "DELETE FROM #{$TB_KOYOMI} WHERE user='#{@user.name}' AND freeze=0 AND ( koyomi='' OR koyomi IS NULL OR DATE IS NULL );" ) unless @user.barrier
  end
end

