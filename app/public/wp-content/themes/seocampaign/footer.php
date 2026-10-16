<?php
/**
 * Site footer.
 *
 * @package SEOcampaign
 */

defined( 'ABSPATH' ) || exit;
?>

<footer class="site-footer">
	<div class="wrap">
		<?php
		wp_nav_menu(
			array(
				'theme_location'       => 'footer',
				'container'            => 'nav',
				'container_aria_label' => __( 'Footer', 'seocampaign' ),
				'fallback_cb'          => false,
				'depth'                => 1,
			)
		);
		?>
		<p class="site-info">&copy; <?php echo esc_html( wp_date( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?></p>
	</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
