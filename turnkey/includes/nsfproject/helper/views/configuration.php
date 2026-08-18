<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/29/26
 * Time: 4:37 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/

foreach($ini as $key => $value)
{
    ?>
    <h2><?php echo $key?></h2>
    <table>
    <?php
    foreach($value as $k => $v) {
        ?>
        <tr>
            <td><?php echo $k; ?></td>
            <?php if (is_array($v)) {
                echo '</tr>';
                foreach($v as $k2 => $v2) {
                    ?>
                    <tr>
                        <td><?php echo $k2+1; ?></td>
                        <td><?php echo (!empty($v2)?$v2:'EMPTY'); ?></td>
                    </tr>
                    <?php
                }
            } else {
            ?>
            <td><?php echo (!empty($v)?$v:'EMPTY'); ?></td>
        </tr>
        <?php
        }
    }
    ?>
    </table>
<?php
}
?>
<a href="<?php echo WEB_PATH;?>/manage/conf/edit">Edit the Configuration File</a>

