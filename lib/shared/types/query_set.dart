part of 'types.dart';

abstract class QuerySet {
  set label(String value);

  QueryType get type;
  int get count;

  void destroy();
  void dispose();
}
