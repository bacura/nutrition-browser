#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 nutrition physical tools 0.10 (2025/04/26)


#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )
@mod_path = 'physique_'

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'
require './brain'
require './body'

#==============================================================================
#DEFINITION
#==============================================================================

#### Menu on line
def menu( user )
	mods = Dir.glob( "#{$HTDOCS_PATH}/#{@mod_path}/mod_*" )
	mods.map! do |x|
		x = File.basename( x )
		x = x.sub( 'mod_', '' )
		x = x.sub( '.rb', '' )
	end

	html = ''
	mods.each.with_index( 1 ) do |e, i|
		require "#{$HTDOCS_PATH}/#{@mod_path}/mod_#{e}.rb"
		ml = module_lp( user.language )
		html << "<span class='btn badge rounded-pill ppill' onclick='PhysiqueForm( \"#{e}\" )'>#{ml[:mod_name]}</span>"
	end

	return html
end

#==============================================================================
# Main
#==============================================================================
user = User.new( @cgi )
db = Db.new( user, @debug, false )

#### Getting POST
mod = @cgi['mod']
html_init( nil ) if @cgi['step'] != 'json'

if @debug
	user.debug
	puts "mod:#{mod}<br>\n"
	puts "<hr>\n"
end


#### Driver
html_module = ''
js_module = ''
if mod == 'menu'
	puts 'MENU<br>' if @debug
	unless user.status == 7
		html_module = menu( user )
	else
		html_module = "<span class='ref_error'>[ginmi]Astral user limit!</span><br>"
	end
else
	if mod == ''
		html_module =  "<div align='center'>Physique assessment tools</div>"
	else
		require "#{$HTDOCS_PATH}/#{@mod_path}/mod_#{mod}.rb"
		html_module = physique_module( @cgi, db ) unless user.status == 7
	end
end
puts 'HTML<br>' if @debug
puts html_module



#==============================================================================
#FRONT SCRIPT
#==============================================================================
if mod == ''
	js = <<-"JS"
<script type='text/javascript'>
var PhysiqueForm = async ( mod ) => {

    // データ描画用のヘルパー関数
    const renderData = ( id, data, hasScripts = false ) => {
        const element = document.getElementById( id );
        if ( !element ) return console.error( `#${id} が見つかりません` );

        if ( !hasScripts ) {
            // 純粋HTML（form用）
            element.innerHTML = data;
            return;
        }

        // HTML+インラインJavaScript（results用、C3.jsチャート）
        const tempDiv = document.createElement( 'div' );
        tempDiv.innerHTML = data;

        // <script>タグを抽出して実行
        tempDiv.querySelectorAll( 'script' ).forEach(( script ) => {
            const newScript = document.createElement('script');
            newScript.textContent = script.textContent; // インラインC3.jsコード
            document.body.appendChild(newScript);
            //document.body.removeChild(newScript);
        });

        // HTMLをターゲット要素に描画
        element.innerHTML = '';
        element.append( ...tempDiv.childNodes );
    };

    try{
        // フォームデータ（100% HTML）
        const formRes = await fetch( '#{myself}', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ mod, step: 'form' }),
        });
        if ( !formRes.ok ) throw new Error( 'フォームデータ取得失敗' );
        const formData = await formRes.text();
        renderData( 'L1', formData, false ); // HTMLのみ

        // 結果データ（HTML+インラインC3.js）
        const resultsRes = await fetch( '#{myself}', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ mod, step: 'results' }),
        });
        if ( !resultsRes.ok ) throw new Error( '結果データ取得失敗' );
        const resultsData = await resultsRes.text();
        renderData( 'L2', resultsData, true ); // HTML+C3.jsスクリプト

        // グローバルフラグと外部関数
        window.dl2 = true;
        displayBW();
    }catch ( error ){
        console.error('エラー:', error );
    }

};

</script>
JS

	puts js 
end