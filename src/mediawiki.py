# mt2mw -- package for migrating a Mindtouch wiki to MediaWiki
# Copyright (C) 2010 Catalyst IT Ltd 

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# system library
import wikitools3 as wt
import psycopg2 as pg
import hashlib
import os
import traceback

class MWWiki:
    def __init__(self, baseurl, username, password, dbconfig=None, dataroot=None):

        self.debug = True
        self.dbconfig = None
        self.site = None
        apiurl = "{0}/api.php".format(baseurl)
        self.username = username
        self.flg_copyfiles = True
        self.flg_copypages = True

        if self.debug:
            msg = "Opening mediawiki url: {0}, {1}".format(baseurl,username)
            print(msg)

        try:
            self.site = wt.wiki.Wiki(apiurl)
        except Exception as e:
            msg = "ERROR: mediawiki {0}".format(e)
            print(msg)
            print(traceback.format_exc())
            
        if self.site:
            try:
                self.site.login(username, password=password, remember=True)
                self.dbconfig = dbconfig
                self.dataroot = dataroot
                if self.dbconfig:
                    print('Database details given: files will be added directly')
                    self.connect_db()
            except Exception as e:
                msg = "ERROR: mediawiki login {0}".format(e)
                print(msg)

    def set_copypages(self, v):
        self.flg_copypages = v
        return self.flg_copypages
    
    def get_copypages(self):
        return self.flg_copypages

    def set_copyfiles(self, v):
        self.flg_copyfiles = v
        return self.flg_copyfiles
    
    def get_copyfiles(self):
        return self.flg_copyfiles

    def connect_db(self):
        try:
            self.db = pg.connect(**self.dbconfig)
        except Exception as e:
            raise e

    @staticmethod
    def subpage_menu(page):
        if page.subpages:
            result = '\n\n===Subpages===\n\n%s' % '\n'.join(list('* [[%s|%s]]' % (s.path, s.title) for s in page.subpages))
            return result.encode('utf-8')
        return ''

    @staticmethod
    def files_list(page):
        if page.files:
            result = '\n\n===Files===\n\n%s' % '\n'.join(list('*[[File:%s]]' % (f.title) for f in page.files))
            return result.encode('utf-8')
        return ''

    def commit_file_db(self, cursor, file):
        filehash = hashlib.md5(file.title).hexdigest()
        path = os.path.join(self.dataroot, filehash[:1], filehash[:2], file.title)
        file.download_to(path)
        filedata = file.get_info()
        filedata['user'] = None
        filedata['user_text'] = self.username
        cursor.execute('''
            INSERT INTO mediawiki.image (
                img_name,
                img_size,
                img_width,
                img_height,
                img_metadata,
                img_bits,
                img_media_type,
                img_major_mime,
                img_minor_mime,
                img_description,
                img_user,
                img_user_text,
                img_timestamp,
                img_sha1
            ) VALUES (
                %(name)s,
                %(size)s,
                %(width)s,
                %(height)s,
                %(metadata)s,
                %(bits)s,
                %(media_type)s,
                %(major_mime)s,
                %(minor_mime)s,
                %(description)s,
                %(user)s,
                %(user_text)s,
                %(timestamp)s,
                %(sha1)s
            );''', filedata
        )
        self.db.commit()


    def write_files_api(self, page):
        if self.site:
            for file in page.files:
                f = wt.wikifile.File(self.site, file.title)
                msg = "Processing file: {0}".format(f.title)
                print(msg)
                try:
                    f.upload(url=file.url)
                    msg = "Uploaded file: {0}".format(f.title)
                    print(msg)
                except Exception as e:
                    msg = "Exception during upload: {0}".format(e)
                    print(msg)
                    print(traceback.format_exc())
        else:
            msg = "ERROR: site is not open".format(self.site)
            print(msg)

    def write_files_db(self, page):
        cursor = self.db.cursor()
        for file in page.files:
            cursor.execute('''
                SELECT img_name FROM mediawiki.image WHERE img_name = %s''',
                (file.title,)
            )
            if not cursor.fetchall():
                self.commit_file_db(cursor, file)
                msg = "Uploaded file: {0}".format(file.title)
                print(msg)
        cursor.close()


    def write(self, page):
        # upload the files for this page
        if page.files and self.flg_copyfiles:
            if self.dbconfig:
                self.write_files_db(page)
            else:
                self.write_files_api(page)
        if self.flg_copypages:
            if self.site:
                    # write the page itself
                    p = wt.page.Page(self.site, title=page.path)
                    try:
                        p.edit(
                            text='%s%s%s' % (
                                page.towiki(),
                                MWWiki.files_list(page),
                                MWWiki.subpage_menu(page)
                            ),
                            skipmd5=True
                        )
                        msg = "Wrote page: {0}".format(p.title)
                        print(msg)
                    except Exception as e:
                        msg = "Exception during write: {0}".format(e)
                        print(msg)
                        print(traceback.format_exc())
            else:
                msg = "ERROR: cannot write page, site is not open".format(self.site)
                print(msg)

    def update_mainpage(self, root):
        if self.flg_copypages:
            if self.site:
    
                p = wt.page.Page(self.site, title='MediaWiki:Mainpage')
                try:
                    p.edit(text=root.title.replace(' ', '_'))
                except Exception as e:
                    print(e)
            else:
                msg = "ERROR: update main page, site is not open".format(self.site)
                print(msg)

    def create_from_mindtouch(self, root):
        self.write(root)
        for subpage in root.subpages:
            self.create_from_mindtouch(subpage)

    def done(self):
        if self.site:
            self.site.logout()
        if self.dbconfig:
            self.db.commit()
            self.db.close()

