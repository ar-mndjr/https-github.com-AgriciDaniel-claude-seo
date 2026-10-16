<?php
/**
 * Fallback template.
 *
 * WordPress uses this file whenever no more specific template exists
 * (page.php, single.php and so on), so it handles every kind of view.
 *
 * @package SEOcampaign
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>

<main id="main" class="site-main">
	<div class="wrap">
		<?php if ( have_posts() ) : ?>
			<?php
			while ( have_posts() ) :
				the_post();
				?>
				<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
					<?php if ( is_singular() ) : ?>
						<?php the_title( '<h1 class="entry-title">', '</h1>' ); ?>
						<div class="entry-content">
							<?php the_content(); ?>
						</div>
					<?php else : ?>
						<?php the_title( '<h2 class="entry-title"><a href="' . esc_url( get_permalink() ) . '">', '</a></h2>' ); ?>
						<?php the_excerpt(); ?>
					<?php endif; ?>
				</article>
				<?php
			endwhile;

			the_posts_pagination();
			?>
		<?php else : ?>
			<p><?php esc_html_e( 'Nothing found.', 'seocampaign' ); ?></p>
		<?php endif; ?>
	</div>
</main>

<?php
get_footer();
