<?php
/**
 * SEOcampaign theme setup.
 *
 * @package SEOcampaign
 */

defined( 'ABSPATH' ) || exit;

/**
 * Registers theme features and menu locations.
 */
function seocampaign_setup() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support(
		'html5',
		array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script', 'navigation-widgets' )
	);

	register_nav_menus(
		array(
			'primary' => __( 'Main menu', 'seocampaign' ),
			'footer'  => __( 'Footer menu', 'seocampaign' ),
		)
	);
}
add_action( 'after_setup_theme', 'seocampaign_setup' );

/**
 * Loads the theme stylesheet.
 */
function seocampaign_enqueue_assets() {
	wp_enqueue_style(
		'seocampaign-main',
		get_theme_file_uri( 'assets/css/main.css' ),
		array(),
		seocampaign_asset_version( 'assets/css/main.css' )
	);
}
add_action( 'wp_enqueue_scripts', 'seocampaign_enqueue_assets' );

/**
 * Returns a cache-busting version for a theme file.
 *
 * Uses the file's last-modified time, so browsers fetch a fresh copy
 * whenever the file changes, locally and after every deploy.
 *
 * @param string $relative_path Path inside the theme folder.
 * @return string
 */
function seocampaign_asset_version( $relative_path ) {
	$file = get_theme_file_path( $relative_path );

	return file_exists( $file ) ? (string) filemtime( $file ) : wp_get_theme()->get( 'Version' );
}
