<form class='pr-filters'>
	<select name="category">
		<?php
			$orderby_options = array(
				'title' => 'Order By Title',
			);
			foreach( $orderby_options as $value => $label ) {
				echo "<option ".selected( $_GET['category'], $value )." value='$value'>$label</option>";
			}
		?>
	</select>

<input type='submit' value='Filter!'>
</form>