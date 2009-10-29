.. couchquery documentation master file, created by
   sphinx-quickstart on Mon Aug 17 21:05:22 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

couchquery -- A Python library for CouchDB
==========================================

.. module:: couchquery
   :synopsis: Simple CouchDB interface.
.. moduleauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>
.. sectionauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>

CouchDB is not a relational database. The purpose of couchquery is to provide a simple, flexible and dynamic interface for creating, updating and deleting documents and working with views.

.. toctree::
   :maxdepth: 3

.. _installation:

Installation
------------

`couchquery` requires `setuptools <http://pypi.python.org/pypi/setuptools>`_ and `httplib2 <http://code.google.com/p/httplib2/>`_. If you do not have them installed already you will want to::

   $ curl -O http://peak.telecommunity.com/dist/ez_setup.py
   $ python ez_setup.py
   $ easy_install -U httplib2

Now you can install couchquery::

   $ easy_install couchquery

The source code is publicly `available on github <http://github.com/mikeal/couchquery>`_. Tickets should be logged on the `github issues tracker <http://github.com/mikeal/couchquery/issues>`_. 

The process for code contributions is for users to `fork the repository on github <http://help.github.com/forking/>`_, push modifications to their public fork, and then send `mikeal <http://github.com/mikeal>`_ a `pull request <http://github.com/guides/pull-requests>`_.

.. _working-with-documents:

Working with Documents
----------------------

Create a :class:`Database` object for any CouchDB database you would like to interact with.

   >>> db = Database('http://localhost:5984/buckaroo')

Create a new document in the database.

   >>> db.create({'type':'red-lectroid','name':'John Whorfin'})
   {u'rev': u'1-4198154595', u'ok': True, u'id': u'c581bbc8fd32f49ecb2f8668ed71fe9b'}
   
After creating a new document you are given the response dict from couch which includes the id of the document. You can also get documents by id.

   >>> info = db.create({'type':'red-lectroid','name':'John Whorfin'})
   >>> doc = db.get(info['id'])
   >>> type(doc)
   <class 'couchquery.Document'>

:class:`Document` objects are just slightly extended dict objects that provide slightly simpler attribute access.

   >>> doc.name
   "John Worfin"
   >>> doc['name']
   "John Worfin"
   >>> doc.location = "The 8th Dimension"
   >>> doc.has_key('location')
   True
   >>> doc.get('fakeattribute', False)
   False
   
When saving documents you must have the latest revision.

   >>> db.update(doc)

If you do not have the latest revision you'll get a :exc:`CouchDBDocumentConflict` exception.

   >>> db.update(old_doc)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "/Users/mikeal/Documents/git/couchquery/couchquery/__init__.py", line 271, in update
       raise CouchDBException(response.body)
   couchquery.CouchDBException: {"error":"conflict","reason":"Document update conflict."}
   
:meth:`Database.create`, :meth:`Database.update` and :meth:`Database.delete` all support bulk operations when :term:`iterable` types are passed.

   db.create([{'type':'red-lectroid', 'name':'John Bigboote'},
              {'type':'red-lectroid', 'name':"John O'Connor"},])
   
.. _creating-views:
   
Creating views
--------------

Futon is great, but I like to check my design documents in to version control so that I can push and pull changes to them from different contributors on github.

With couchquery you can create a single directory for each design document where each subdirectory is a view in that design document. Inside the view directories you write a map.js and optional reduce.js file which contains your view functions::

   $ du -a views          
   32      views
   8       views/lectroidByType                                                            
   8       views/lectroidByType/map.js
   8       views/byType
   8       views/byType/map.js
   8       views/byType/reduce.js

You can then "sync" this directory as a design document in your database.::

   db.sync_design_doc('banzai', os.path.join(os.path.dirname(__file__), 'views'))

Now your directory of views is a design document in the database.

.. _working-with-views:

Working with views
------------------

The couchquery views API is simple and straight forward provided you already have some understanding of how CouchDB views work.::

   db.views.banzai.lectroidByType(key="red-lectroid")

The view API provides functions for each view that accept keyword arguments which are then converted in to query string arguments to the CouchDB HTTP View API.

These view functions return :class:`RowSet` objects for each view result. :class:`RowSet` objects are one of the major highlights of couchquery. A RowSet object represents the **result** of a CouchDB query, it is not an abstraction of the query itself.::

   rows = db.views.banzai.lectroidByType(key="red-lectroid")

Iterating over a :class:`RowSet` object yields the values from the view result. If the values are documents then it will yield a Document instance for the value.::

   for doc in rows:
       if "lectroid" in doc.type:
           doc.species = 'lectroid'
   rows.save()
   
You can use :meth:`RowSet.save()` to save all changes made to the values in the :class:`RowSet` provided the values are documents.::

   >>> type(rows[0])
   <class 'couchquery.Document'>
   >>> type(rows['red-lectroid'])
   <class 'couchquery.RowSet'>

You can get a value in the :class:`RowSet` by position using list style syntax. Dictionary syntax allows you to get new :class:`RowSet` objects for the selection of rows in the result that matched the given key, this is useful when doing range queries because you can get subsets of the range without making additional queries to the server.::

   >>> rows = db.views.banzai.lectroidByType(startkey=None, endkey={})
   >>> red_lectroids = rows['red-lectroid']
   >>> black_lectroids = rows['black-lectroid']

When applicable, properties like RowSet.offset are preserved and calculated for the new RowSet instance.::
   
   >>> rows.offset
   0
   >>> red_lectroids.offset
   2
   >>> black_lectorids.offset
   0

RowSet objects only assume that values are Documents if they have _id attributes. If not, the value itself is returned by all these value APIs.

RowSet objects also have convenient methods for working with the ids and keys, or more explicitly with values.::

   >>> type(rows.keys())
   <type 'list'>
   >>> type(rows.ids())
   <type 'list'>
   >>> type(rows.values())
   <type 'list'>

Another convenient method is :meth:`items` which returns a list of (key, value) tuples for the keys and values in the view result.::

   for key, value in rows.items():
       if 'lectroid' in key:
           assert 'John' in value.name

The contains operations are also customized. String values are checked against the id's in the result while other objects are checked against the values.

   >>> info = db.create({'type':'black-lectroid', 'name':'John Parker'})
   >>> red_lectroids = db.views.banzai.lectroidByType(key='red-lectroid')
   >>> info['id'] in red_lectroids
   False
   >>> black_lectroids = db.views.banzai.lectroidByType(key='black-lectroid')
   >>> info['id'] in black_lectroids
   True
   >>> db.get(info['id']) in black_lectroids
   True


:mod:`couchquery` --- Simple CouchDB module.
======================================================================

.. attribute:: debugging

   Defaults to :const:`True`. When set to :const:`True` accessing most dynamic attributes will be
   validated with *HTTP HEAD* requests for the resources. This incurs additional delay in accessing most 
   views for the first time but results in more accurate exceptions. 

.. class:: Database(uri[, http[, http_engine[, cache]]])

   *uri* is the full http uri to the CouchDB database.
   
   *http* can be an instance of :class:`httplib2.Http` or an instance of one of the 
   :class:`HttpClient` subclasses. The default is to create an instance of :class:`Httplib2Client` 
   for the given uri.
   
   *cache* is an argument specifically passed to :class:`httplib2.Http`, it is special cased for reverse 
   compatibility with an older version of this API.
   
   .. method:: get(_id)
      
      Get a single document by *_id* from the database.
   
      Returns a :class:`Document` object for the given *_id* in the database.
      
   .. method:: create(doc[, all_or_nothing])
   
      Create a document. Accepts any object that can be converted in to a dict.
      If multiple documents are passed they are handed off to the bulk document handler.
      
      Uses the HTTP POST interface for creating documents in CouchDB. If :func:`list`, :func:`tuple` or 
      :class:`types.GeneratorType` types are passed then the creation is handed off to 
      :func:`Database.bulk` with *all_or_nothing* passed as well. *all_or_nothing* defaults to 
      :const:`False`.
   
   .. method:: update(doc[, all_or_nothing])
   
      Update a document. Accepts any object that can be converted in to a dict.
      If multiple documents are passed they are handed off to the bulk document handler.
      
      Uses the HTTP PUT interface for updating documents in CouchDB.  If :func:`list`, :func:`tuple`, 
      :class:`types.GeneratorType` or :class:`RowSet` types are passed then the update is handed off to 
      :func:`Database.bulk` with *all_or_nothing* passed as well. *all_or_nothing* defaults to 
      :const:`False`.
   
   .. method:: delete(doc[, all_or_nothing])
   
      Delete a document. Accepts any object that can be converted in to a dict.
      Document/s must contain _id and _rev properties.
      If multiple documents are passed they are removed using the bulk document API.

      Uses the HTTP DELETE interface for updating documents in CouchDB.  If :func:`list`, :func:`tuple`, 
      :class:`types.GeneratorType` or :class:`RowSet` types are passed then the delete is handed off to 
      :meth:`bulk` with *all_or_nothing* passed as well. *all_or_nothing* defaults to 
      :const:`False`.
      
   .. method:: save(doc[, all_or_nothing])
   
      Smart save method. Hands off to bulk, create, or update.
      
      If :func:`list`, :func:`tuple`, :class:`types.GeneratorType` or :class:`RowSet` types are passed
      they are handed off to :func:`Database.bulk`. If the object represents a single document then it is 
      checked for the *_id* item and if accessible then it is passed to `update` if not then it is sent 
      to `create`. *all_or_nothing* defaults to :const:`False`.
      
   .. method:: sync_design_doc(name, path)
   
      Sync a directory structure with proper map.js and reduce.js files at `path` as a desing document
      named `name`. Document above in :ref:`creating-views` 
      
   .. attribute:: views
   
      Instance of :class:`Views` for this CouchDB Database.
   
.. function:: createdb(db)

   Accepts either an instance of :class:`Database` or a uri to the database. Will cause an HTTP PUT 
   request to create the new database, validate the response code, and return you decoded response body.
   
.. function:: deletedb(db)
   
   Accepts either an instance of :class:`Database` or a uri to the database. Will cause an HTTP DELETE 
   request to remove database, validate the response code, and return you decoded response body.
   
.. class:: Document([*args[, **kwargs]])
   
   Subclass of :func:`dict`. __setattr__, __getattr__ and __delattr__ are linked to __setitem__, 
   __getitem__ and __delitem__ respectively to support a shorter attribute access and manipulation
   syntax.
   
.. class:: Views(db)

   CouchDB Views API. 
   
   Requires a :class:`Database` instance.
   
   Supports dynamic attribute access for design document containers by name.::
   
      >>> type(db.views.bonzai)
      <class 'couchquery.Design'>
   
   The design document is checked to be valid via an HTTP HEAD request if :attr:`debugging` is set.
   
   .. method:: all([include_docs[, startkey[, endkey[, keys]]]])
   
      Interface for the CouchDB _all_docs HTTP REST API.
      
      include_docs defaults to :const:`True`. keys, startkey, and endkey all default to :const:`None` and 
      are not used unless set to a value other than None.
      
      Returns a :class:`RowSet` instance for the returned results. The values in the :class:`RowSet` are 
      set to  the docuemnts when include_docs is :const:`True` to make the returned result closer to a 
      standard view result.
      
   .. method temp_view(map[, reduce[, **kwargs]])

      Creates a temp view and returns a :class:`RowSet` object for the given query against it.
      
      All HTTP view arguments are accepted as keyword arguments. Optionally pass reduce method.
      
      `map` and `reduce` arguments should be strings that can be `eval()` in to proper JavaScript 
      functions.
      
.. class:: Design(db, _id)
      
   Represents access to a given Design document. Part of the View access API document in 
   :ref:`working-with-views`.
   
   This object has customized attribute access which returns a :class:`View` object for a view 
   in the design document of the given `name`.
      
      >>> type(db.views.bonzai.lectroidByType)
      <class 'couchquery.View'>
      
.. class:: View(db, _id)

   A :func:`callable` class which provides access to a given view using the CouchDB HTTP View API.
   
   .. method:: __call__([**kwargs]):
   
      Queries a CouchDB view.
      
      If `keys` is in kwargs this uses the HTTP POST API, if `keys` is not in kwargs the HTTP GET API 
      is used. 
      
      Additional keyword arguments are passed as arguments to the noted HTTP API. All arguments
      except `key_docid`, `startkey_docid`, `endkey_id` and `stale` will be JSON serialized.
      
      Returns a :class:`RowSet` object for the returned result.

.. class:: RowSet(db, rows[, offset[, total_rows[, parent]]])

   View result abstraction. Supports bulk edits, and a variety of other features documented in
   :ref:`working-with-views`.
   
   Iterating over a RowSet will iterate over the values in the view result. Values that are documents 
   will be turned in to :class:`Document` instances.
   
   .. method:: ids()
   
      Returns a list of all ids in the view result.
      
   .. method:: keys()
   
      Returns a list of all the keys in the view result.
   
   .. method:: values()
   
      Returns a list of all the values in the view result.
   
   .. method:: items([key[, value]])
      
      Return a list of (key, value) tuples. By default `key` is `"key"` and `value` is `"value"` which 
      means it will return a pair of `(row['key'], row['value'],)` for every `row` in the view result.
         
   .. attribute:: offset
   
      Offset for the rows in the view result relative to all keys in the view.
      
   .. method:: get_offset(obj[, key])
   
      Returns the offset for the given object. `key` defaults to `"value"` which means that obj is 
      compared against the values in the rows. If the object exists multiple times the offset for the
      first occurence will be returned.
   
   .. method:: save()
   
      Save all the change made to the values in this RowSet. Sends this RowSet instance to 
      :meth:`Database.bulk`.
   
   .. method:: delete()
   
      Remove all the values in this :class:`RowSet` from the database. Sends this RowSet instance to
      :meth:`Database.delete`.
      
      
      
      