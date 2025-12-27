#Nutrition browser 2020 body 0.1.1 (2025/12/19)

#==============================================================================
#STATIC
#==============================================================================


#==============================================================================
# LIBRARY
#==============================================================================
require 'fileutils'
require 'time'


#==============================================================================
#DEFINITION
#==============================================================================

#### Isolation photo init
def iso_init( cookie )
  puts "Content-type: image/jpeg\n"
  puts "Cache-Control: no-store, no-cache, must-revalidate, max-age=0\n"
  puts "Cache-Control: post-check=0, pre-check=0, false\n"
  puts "Pragma: no-cache\n"
  puts cookie unless cookie == nil
  puts "\n"
end


class Bio
  attr_accessor :sex, :birth, :age, :height, :weight, :kexow, :pgene

  def initialize( user )
    @user = user
    res = $DB.prepare( "SELECT bio FROM #{$TB_CFG} WHERE user=?" ).execute( @user.name )&.first
    if res['bio']&.to_s.empty?

      begin
        bio = JSON.parse( res['bio'] )
      rescue JSON::ParserError => e
        puts "J(x_x)pE: #{e.message}<br>"
        exit
      end     
 
      @sex = bio['sex'].to_i
      @birth = Time.parse( bio['birth'] )
      @height = bio['height'].to_f * 100
      @weight = bio['weight'].to_f
      @kexow = bio['kexow'].to_i
      @pgene = bio['pgene'].to_i
      @age = ( Date.today.strftime( "%Y%m%d" ).to_i - @birth.strftime( "%Y%m%d" ).to_i ) / 10000
    end
  end

  def kex_ow()
    res = $DB.prepare( "SELECT koyomi FROM #{$TB_CFG} WHERE user=?" ).execute( @user.name )&.first
    if res && @kexow == 1

      begin
        koyomi = JSON.parse( res['koyomi'] )
      rescue JSON::ParserError => e
        puts "J(x_x)pE: #{e.message}<br>"
        exit
      end     

      kex_select = koyomi['kex_select']
      0.upto( 9 ) do |c|
        @height = kex_select[c.to_s].to_f * 100 if kex_select[c.to_s] == 'HEIGHT'
        @weight = kex_select[c.to_s].to_f if kex_select[c.to_s] == 'WEIGHT'
      end
    end
  end

  def debug()
    puts @sex, @birth, @age, @height, @weight, @kexow, @pgene
  end
end


####
class Calendar
  attr_accessor :yyyy, :yyyyf, :mm, :mms, :dd, :dds, :ddl, :wd, :wf, :wl

  def initialize( user, yyyy = 0, mm = 0, dd = 0 )
    @user = user
    @yyyy = yyyy
    @mm = mm
    @dd = dd

    if yyyy == 0
      @date = Date.today
      @yyyy = @date.year
      @mm = @date.month
      @dd = @date.day
    else
      @date = Date.new( @yyyy, @mm, @dd )
    end

    #sub items
    @wd, @wf, @ddl, @wl, @mms, @dds = update_sub( @date )

    @yyyyf = Time.now.year
    res = $DB.prepare( "SELECT koyomi FROM #{$TB_CFG} WHERE user=?" ).execute( @user.name )&.first
    unless res['koyomi']&.to_s.empty?

      begin
        koyomi = JSON.parse( res['koyomi'] )
      rescue JSON::ParserError => e
        puts "J(x_x)pE: #{e.message}<br>"
        exit
      end     

      @yyyyf = koyomi['start']
    end
  end

  def move_yyyy( yyyy )
    p @date.year
    @date = @date.next_year( yyyy.to_i )
    @date += 1
    p @date.year
    @wd, @wf, @ddl, @wl, @mms, @dds = update_sub( @date )
  end

  def move_mm( mm )
    @date = @date.next_month( mm.to_i )
    @date += 1
    @wd, @wf, @ddl, @wl, @mms, @dds = update_sub( @date )

  end

  def move_dd( dd )
    @date += dd.to_i
    @wd, @wf, @ddl, @wl, @mms, @dds = update_sub( @date )
  end

  def ym()
    return "#{@date.year}-#{@mms}"
  end

  def ymd()
    return "#{@date.year}-#{@mms}-#{@dds}"
  end

  def ymdf()
    return "#{@date.year}-#{@mms}-01"
  end

  def ymdl()
    return "#{@date.year}-#{@mms}-#{@ddl}"
  end

  def debug()
    puts "calender.yyyy:#{@yyyy}<br>"
    puts "calender.yyyyf:#{@yyyyf}<br>"
    puts "calender.mm:#{@mm}<br>"
    puts "calender.dd:#{@dd}<br>"
    puts "calender.ddl:#{@ddl}<br>"
    puts "calender.wf:#{@wf}<br>"
    puts "calender.wl:#{@wl}<br>"
  end

  private

  def update_sub( date_ )
    #today's week
    wd = Date.new( date_.year, date_.month, date_.day ).wday

    #1st day's week
    wf = Date.new( date_.year, date_.month, 1 ).wday

    #The last day
    ddl = Date.new( date_.year, date_.month, -1 ).day

    #The last day's week
    wl = Date.new( date_.year, date_.month, ddl ).wday

    mms = date_.month < 10 ? "0#{date_.month}" : date_.month.to_s
    dds = date_.day < 10 ? "0#{date_.day}" : date_.day.to_s

    return wd, wf, ddl, wl, mms, dds
  end
end


class Media
  attr_accessor :user, :owner, :code, :series, :base, :origin, :alt, :type, :date, :zidx

  def initialize( user, base = nil )
    @code = nil
    @user = user
    @owner = nil
    @base = base
    @origin = nil
    @type = nil
    @alt = nil
    @date = nil
    @zidx = 0
    @secure = 0

    @series = []
    @bases = []
    @flesh = true
    @flesh = false if @user.status == 7

    res = $DB.prepare( "SELECT COUNT(code), MIN(date), MAX(date) FROM #{$TB_MEDIA} WHERE user=?" ).execute( @user.name )&.first
    if res
      @count = res['COUNT(code)']
      @t = res['MIN(date)']
      if @t
        @yyyy_min = @t.strftime( "%Y" ).to_i
      else
        @yyyy_min = 0
      end
      @t = res['MAX(date)']
      if @t
        @yyyy_max = @t.strftime( "%Y" ).to_i
      else
        @yyyy_max = 0
      end
    end

    @l = {
      'camera'  => "<img src='bootstrap-dist/icons/camera.svg' style='height:1.2em; width:1.2em;'>",\
      'trash'   => "<img src='bootstrap-dist/icons/trash-fill.svg' style='height:1.2em; width:1.2em;'>",\
      'left-ca' => "<img src='bootstrap-dist/icons/arrow-left-circle.svg' style='height:1.2em; width:1.2em;'>",\
      'right-ca'  => "<img src='bootstrap-dist/icons/arrow-right-circle.svg' style='height:1.2em; width:1.2em;'>"
    }
  end


  def load_db()
    res = $DB.prepare( "SELECT * FROM #{$TB_MEDIA} WHERE code=?" ).execute( @code )&.first
    if res
      @owner = res['user'].to_s
      @base = res['base'].to_s
      @origin = res['origin'].to_s
      @type = res['type'].to_s
      @alt = res['alt'].to_s
      @date = res['date']
      @zidx = res['zidx'].to_i
      @secure = res['secure'].to_i
    else
      puts "<span class='error'>[Media load]ERROR!!<br>"
      puts "code:#{@code}</span><br>"
    end
  end

  def load_cgi( cgi )
    @code = cgi['code'].to_s
    @base = cgi['base'].to_s
    @origin = cgi['origin'].to_s
    @type = cgi['type'].to_s
    @alt = cgi['alt'].to_s
    @date = cgi['date']
    @zidx = cgi['zidx']
    @zidx = 0 unless @zidx
    @secure = cgi['secure'].to_i
    @secure = 0 unless @secure
  end

  def save_db()
    if @code
      @zidx = @series.size
      $DB.prepare( "INSERT INTO #{$TB_MEDIA} SET user=?, code=?, base=?, origin=?, type=?, alt=?, date=?, zidx=?, secure=?" ).execute( @user.name, @code, @base, @origin, @type, @alt, @date, @zidx, @secure ) unless @user.barrier
    end
  end

  def delete_db( real )
    if @code
      if real
        $DB.prepare( "DELETE FROM #{$TB_MEDIA} WHERE user=? AND code=?" ).execute( @user.name, @code ) unless @user.barrier
      else
        $DB.prepare( "UPDATE #{$TB_MEDIA} SET base=? WHERE user=? AND code=?" ).execute( 'lost', @user.name, @code ) unless @user.barrier
      end
    end
  end

  def get_series()
    unless @origin.to_s.empty?
      res = $DB.prepare( "SELECT * FROM #{$TB_MEDIA} WHERE origin=? AND base=? ORDER BY zidx" ).execute( @origin, @base )
      @owner = res.first['user'] if res.first
      @series = []
      res.each do |e| @series << e['code'] end
    end

    return @series
  end

  def get_count()
    return @count
  end

  def get_yyyy()
    return @yyyy_min, @yyyy_max
  end


  def secure()
    if @secure == 1
      return true
    else
      return false
    end
  end

  def get_bases()
    @bases = []
    res = $DB.prepare( "SELECT DISTINCT base FROM #{$TB_MEDIA} WHERE user=?" ).execute( @user.name )
    res.each do |r| @bases << r['base'] end

    return @bases
  end


  def get_path_code()
    if @secure == 1
      return "#{$SPHOTO_PATH}/#{@code}"
    else
      return "#{$PHOTO_PATH}/#{@code}"
    end
  end


  def move_series()
    if @series.size > 1
      @series.delete( @code )
      @series.insert( @zidx.to_i, @code )
      @series.each.with_index do |e, i|
        $DB.prepare( "UPDATE #{$TB_MEDIA} SET zidx=? WHERE code=? AND origin=? AND base=?" ).execute( i, e, @origin, @base ) unless @user.barrier
      end
    end
  end

  def delete_series( real )
    if @flesh && @series.size > 0
      if real
        case @type
        when 'jpg', 'jpeg', 'png'
          path = @secure == 1 ? $SPHOTO_PATH : $PHOTO_PATH

          @series.each do |e|
            File.unlink "#{path}/#{e}-tns.jpg" if File.exist?( "#{path}/#{e}-tns.jpg" )
            File.unlink "#{path}/#{e}-tn.jpg" if File.exist?( "#{path}/#{e}-tn.jpg" )
            File.unlink "#{path}/#{e}.jpg" if File.exist?( "#{path}/#{e}.jpg" )
          end
        end
        $DB.prepare( "DELETE FROM #{$TB_MEDIA} WHERE user=? AND origin=? AND base=?" ).execute( @user.name, @origin, @base ) unless @user.barrier
      else
        $DB.prepare( "UPDATE #{$TB_MEDIA} SET base=? WHERE user=? AND origin=? AND base=?" ).execute( 'lost', @user.name, @origin, @base ) unless @user.barrier
      end
    end
  end

  def html_series( tn, size, protect )
    html = ''
    if @series.size > 0
      html << "<div class='row'>"
      @series.each.with_index( 0 ) do |e, i|
        html << "<div class='col'>"
        unless protect == 1
          html << "<span onclick=\"photoMove( '#{e}', '#{i - 1}' )\">#{@l['left-ca']}</span>" if i != 0
          html << "&nbsp;&nbsp;<span onclick=\"photoMove( '#{e}', '#{i + 1}' )\">#{@l['right-ca']}</span>" if i != @series.size - 1
        end
        html << '<br>'
        html << "<img src='#{$PHOTO}/#{e}#{tn}.jpg' width='#{size}px' class='img-thumbnail' onclick=\"modalPhoto( '#{e}' )\"><br>"
        unless protect == 1
          html << "<span onclick=\"photoDel( '#{e}' )\">#{@l['trash']}</span>"
        end
        html << "</div>"
      end
      html << "</div>"
    else
      html << 'No photo'
    end

    return html
  end

  def html_series_mini()
    html = ''
    @series.each do |e|
      if e['secure'] == 1
        html << "<img src='photo.cgi?iso=Q&code=#{e}&tn=-tns' class='img-thumbnail' onclick=\"modalPhoto( '#{e}' )\">"
      else
        html << "<img src='#{$PHOTO}/#{e}-tns.jpg' class='img-thumbnail' onclick=\"modalPhoto( '#{e}' )\">"
      end
    end

    return html
  end

  def html_form_generic( enabled )
    html = "<form method='post' enctype='multipart/form-data' id='#{@base}_puf'>"
    html << '<div class="input-group input-group-sm">'
    html << "<label class='input-group-text' for='photo'><img src='bootstrap-dist/icons/camera.svg' style='height:1.2em; width:1.2em;'></label>"
    if enabled
      html << "<input type='file' class='form-control' id='photo' name='photo' onchange=\"PhotoUpload()\">"
    else
      html << "<input type='file' class='form-control' id='photo' DISABLED>"
    end
    html << '</div></form>'

    return html
  end

  def save_photo( cgi )
    tmp_file = cgi['photo'].original_filename
    photo_type = cgi['photo'].content_type
    photo_body = cgi['photo'].read
    photo_size = photo_body.size.to_i

    @code = generate_code( @user.name, 'p' )
    @date = Time.now.strftime( "%Y-%m-%d %H:%M:%S" )
    if photo_type == 'image/jpeg' || photo_type == 'image/jpg'
      @type = 'jpeg'
      ex = 'jpg'
    elsif photo_type == 'image/png'
      @type = 'png'
      ex = 'png'
    else
      @type = nil
    end

    path = @secure == 1 ? $SPHOTO_PATH : $PHOTO_PATH

    if photo_size < $SIZE_MAX && @type != nil && @flesh
      f = open( "#{$TMP_PATH}/#{tmp_file}", 'w' )
      f.puts photo_body
      f.close

      # thumbnail (small)
      ok = system( "vipsthumbnail #{$TMP_PATH}/#{tmp_file} -s #{$TN_SIZE} -o #{path}/#{@code}-tn.jpg" )
      raise "vipsthumbnail tn failed" unless ok

      # thumbnail (smaller)
      ok = system( "vipsthumbnail #{$TMP_PATH}/#{tmp_file} -s #{$TNS_SIZE} -o #{path}/#{@code}-tns.jpg" )
      raise "vipsthumbnail tns failed" unless ok

      # main image (max size)
      ok = system( "vipsthumbnail #{$TMP_PATH}/#{tmp_file} -s #{$PHOTO_SIZE_MAX} -o #{path}/#{@code}.jpg" )
      raise "vipsthumbnail main failed" unless ok

      File.unlink "#{$TMP_PATH}/#{tmp_file}" if File.exist?( "#{$TMP_PATH}/#{tmp_file}" )
    end
  end

  def delete_photo( real )
    return unless @flesh && real && @code != nil

    path = @secure == 1 ? $SPHOTO_PATH : $PHOTO_PATH

    File.unlink "#{path}/#{@code}-tns.jpg" if File.exist?( "#{path}/#{@code}-tns.jpg" )
    File.unlink "#{path}/#{@code}-tn.jpg" if File.exist?( "#{path}/#{@code}-tn.jpg" )
    File.unlink "#{path}/#{@code}.jpg" if File.exist?( "#{path}/#{@code}.jpg" )
  end

  def debug()
    puts "user:#{@user.name}<br>"
    puts "code:#{@code}<br>"
    puts "base:#{@base}<br>"
    puts "origin:#{@origin}<br>"
    puts "type:#{@type}<br>"
    puts "zidx:#{@zidx}<br>"
    puts "alt:#{@alt}<br>"
    puts "date:#{@date}<br>"
    puts "series:#{@series}<br>"
    puts "<hr>"
  end
end
