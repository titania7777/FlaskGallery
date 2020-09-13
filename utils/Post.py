import io
from utils.Settings import page_imgs
from utils.Connector import Connector
from utils.Image import img_compressor_byte, remove_image

class GalleryPost(Connector):
    def __init__(self, page_config):
        super().__init__()
        page_config.set(info_db_connection = self.db_connection)

    def write(self, image, image_path, title, updated):
        sql = "INSERT INTO post_gallery (image, title, updated) values (%s, %s, %s)"
        self.cursor.execute(sql, (image_path, title, updated, ))
        self.conn.commit()

        # save image in local
        img_compressor_byte(io.BytesIO(image.read()), image_path)

    def read(self, image_id):
        sql = "SELECT * FROM post_gallery WHERE pgid=%s"
        self.cursor.execute(sql, (image_id, ))
        result = self.cursor.fetchone()
        return result

    def modify(self, image, image_id, old_image_path, image_path, title, updated):
        sql = "UPDATE post_gallery SET image=%s, title=%s, updated=%s WHERE pgid=%s"
        self.cursor.execute(sql, (image_path, title, updated, image_id, ))
        self.conn.commit()
        
        # save image in local
        img_compressor_byte(io.BytesIO(image.read()), image_path)

        # remove image in local
        remove_image(old_image_path)
    
    def modify_title(self, image_id, title, updated):
        sql = "UPDATE post_gallery SET title=%s, updated=%s WHERE pgid=%s"
        self.cursor.execute(sql, (title, updated, image_id, ))
        self.conn.commit()

    def delete(self, image_id, image_path):
        sql = "DELETE FROM post_gallery WHERE pgid=%s"
        self.cursor.execute(sql, (image_id, ))
        self.conn.commit()

        # remove image in local
        remove_image(image_path)

    def read_page(self, page):
        start = (page-1) * page_imgs + 1
        last = page * page_imgs
        return self.read_range(start, last)

    def read_range(self, start, last):
        sql = "SELECT pgid, title, image, created, updated FROM (SELECT @rownumber := @rownumber + 1 AS rownumbers, pg.* FROM post_gallery AS pg, (SELECT @rownumber := 0) row ORDER BY created DESC) AS pg WHERE rownumbers BETWEEN %s AND %s"
        self.cursor.execute(sql, (start, last, ))
        results = self.cursor.fetchall()
        return results
    
    def get_page_length(self):
        sql = "SELECT count(*) FROM post_gallery"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()[0]

        if result == 0:
            result = 1

        if (result % page_imgs) == 0:
            result = result - 1

        result = int(result / page_imgs) + 1
        return result

    def __del__(self):
        self.close()


class BoardPost(Connector):
    def __init__(self, page_config):
        super().__init__()
        page_config.set(info_db_connection = self.db_connection)

    def write(self):
        pass

    def read(self):
        pass

    def modify(self):
        pass
    
    def delete(self):
        pass

    def __del__(self):
        self.close()