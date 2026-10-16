<?php
/**
 * Plugin Name:       SEOcampaign Tools
 * Description:       Free interactive SEO tools for the SEOcampaign website. Works with any theme.
 * Version:           0.1.0
 * Requires at least: 6.8
 * Requires PHP:      8.2
 * Author:            SEOcampaign
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       seocampaign-tools
 *
 * @package SEOcampaign_Tools
 */

defined( 'ABSPATH' ) || exit;

define( 'SEOCAMPAIGN_TOOLS_VERSION', '0.1.0' );
define( 'SEOCAMPAIGN_TOOLS_DIR', plugin_dir_path( __FILE__ ) );
define( 'SEOCAMPAIGN_TOOLS_URL', plugin_dir_url( __FILE__ ) );

// Each tool is added from includes/ (PHP) and tools/<tool-slug>/ (JS and CSS) as it is built.
