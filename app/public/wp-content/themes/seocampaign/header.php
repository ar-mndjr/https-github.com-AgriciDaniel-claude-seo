<?php
/**
 * Site header: document head, skip link and main navigation.
 *
 * @package SEOcampaign
 */

defined( 'ABSPATH' ) || exit;
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#main"><?php esc_html_e( 'Skip to content', 'seocampaign' ); ?></a>

<header class="site-header">
	<div class="wrap">
		<a class="site-brand" href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home"><?php bloginfo( 'name' ); ?></a>
		<?php
		wp_nav_menu(
			array(
				'theme_location'       => 'primary',
				'container'            => 'nav',
				'container_aria_label' => __( 'Main', 'seocampaign' ),
				'fallback_cb'          => false,
				'depth'                => 1,
			)
		);
		?>
	</div>
</header>
